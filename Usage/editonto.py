# THIS FILE IS PART OF Py2ONTO PROJECT
# Py2ONTO-Edit: A Python-based Tool for Ontology Term Extraction and Translation
#
# THIS PROGRAM IS OPENSOURCE SOFTWARE, IS LICENSED UNDER LGPL-3.0 license
#
# IN THIS PROGRAM WE USED OTHER OPEN SOURCE PROGRAM AND Translate Services:
# DeepL API: https://www.deepl.com/zh/pro-api/
# ChatGLM-130B API: https://bigmodel.cn/
# Gemini API: https://ai.google.dev/
# Owlready2: https://bitbucket.org/jibalamy/owlready2
# Owlready2: LGPL-3.0 license, https://bitbucket.org/jibalamy/owlready2/src/master/LICENSE.txt
# argos-translate, MIT License, https://github.com/argosopentech/argos-translate
# HumanDiseaseOntology: CC0-1.0, https://github.com/DiseaseOntology/HumanDiseaseOntology
# ExcelDNA: zLib license, Copyright (C) 2005-2020 Govert van Drimmelen
# EFO: https://www.ebi.ac.uk/efo/
# SEE FILE LICENSE IN LICENSE FOLDER
#

# coding:utf-8
import os
import argparse
import time

from owlready2 import *
#import requests
import json
from requests.cookies import RequestsCookieJar
import random
import hashlib
import urllib
import http.client
from pandas import read_csv, read_excel, DataFrame, concat, Series, isna

#from translate import Translator  # todo 废弃
# 本地翻译
import argostranslate.package
import argostranslate.translate
from tqdm import tqdm

import google.generativeai as genai
from zhipuai import ZhipuAI
import deepl
import yaml

# 添加多种语言翻译，目前只支持三种，英文-中文，英文-法语，英文-德语
# 英文-中文：en2zh
# 英文-法语：en2fr
# 英文-德语：en2de
class TRANSLATE(object):
    def __init__(self, translation_mode):
        self.translation_mode = translation_mode
        # 设置prompt
        if translation_mode == 'en2zh':
            self.from_code = "en"
            self.to_code = "zh"
            self.trans_prompt = "You are a translate assistant. please translate the following data into Chinese. Only provide the translation, without any explanations:"
        elif translation_mode == 'en2fr':
            self.from_code = "en"
            self.to_code = "fr"
            self.trans_prompt = "You are a translate assistant. Please translate the following data into French. Only provide the translation, without any explanations:"
        elif translation_mode == 'en2de':
            self.from_code = "en"
            self.to_code = "de"
            self.trans_prompt = "You are a translate assistant. Please translate the following data into German. Only provide the translation, without any explanations:"

        # 加载argos本地模型
        if not self.load_argos_model():
            raise FileNotFoundError(f"Model path not found!")

        pass

    def get_argosmodel_files(self, folder_path):
        argosmodel_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".argosmodel"):
                    argosmodel_files.append(os.path.join(root, file))
        return argosmodel_files

    # load argos model
    def load_argos_model(self):
        load_flag = False
        #获取argos files path
        argosmodel_files = self.get_argosmodel_files('./models/')

        if len(argosmodel_files) <= 0:
            raise FileNotFoundError("Please download argos models into models-folder")
        else:
            argostranslate.package.install_from_path(argosmodel_files[0])
            load_flag = True
        return load_flag


    # 使用deeplAPI
    # 需要验证
    def deepl_api(self, content, auth_key='af75f07e-821e-4724-9300-2748eaa809ea:fx'):
        if len(auth_key) == 0:
            raise ValueError("Missing API keys of deepl")
        translator = deepl.Translator(auth_key)
        if self.translation_mode == 'en2zh':
            result = translator.translate_text(content, target_lang="ZH")
        elif self.translation_mode == 'en2fr':
            result = translator.translate_text(content, target_lang="FR")
        elif self.translation_mode == 'en2de':
            result = translator.translate_text(content, target_lang="DE")
        # print(result.text)
        time.sleep(2)
        return result.text

    # 使用GLM130B LLMs进行翻译
    # 默认GLM4，可选GLM3
    def glm_api(self, params, api_key, model_name):
        if len(api_key) == 0:
            raise ValueError("Missing API keys of glm")
        cn_params = params
        #prompt = "You are a translate assistant. Please translate the following data into Chinese, only translation, no explanation:"
        prompt = self.trans_prompt
        try:
            client = ZhipuAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model_name,  # 填写需要调用的模型名称
                messages=[
                    {
                        "role": "user",
                        "content": prompt + params
                    }
                ],
            )
            print(response.choices[0].message.content)
            cn_params = response.choices[0].message.content
        except Exception as e:
            print(e)
        return cn_params

    # Gemini Pro
    # default model is Gemini pro
    def gemini_api(self, params, api_key, model_name):
        if len(api_key) == 0:
            raise ValueError("Missing API keys of gemini")
        cn_params = params
        #prompt = "You are a translate assistant. Please translate the following data into Chinese, only translation, no explanation:"
        prompt = self.trans_prompt

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=model_name)
            reponse = model.generate_content(prompt + params)
            print(reponse.text)
            cn_params = reponse.text
            time.sleep(1)
        except Exception as e:
            print(e)
        return cn_params

    # 机器翻译，粗略翻译
    def local_translate(self, term):
        cn_term = argostranslate.translate.translate(term, self.from_code, self.to_code)
        return cn_term


class EDIT_ONTO(object):
    def __init__(self, owl_path):
        self.owl_path = owl_path
        self.onto = get_ontology(self.owl_path).load()
        self.cut_save_path = ''
        self.owl2csv_path = 'result/part_onto.csv'
        self.translate2csv_dir = ''
        self.add_owl_path = ''
        # assert self.onto != None, "Please enter an available ontology path"
        # sync_reasoner()
        # self.all_class = []
        self.temp_class = []
        self.new_onto = None
        self.entities = []
        self.relations = []
        # 存储owl term context
        self.all_class_with_context = []

    # 读取OWL格式文件
    def get_owl(self, owl_path):
        return get_ontology(owl_path)

    # 获取某节点下本体的所有类
    def __get_all_class(self, root_class):
        if len(list(root_class.subclasses())) > 0:
            for item in root_class.subclasses():
                self.__get_all_class(item)
        self.temp_class.append(root_class)

    # 删除非特指列表中的类
    def __del_class_not_in_list(self, root_class, cut_class_list):
        if len(list(root_class.subclasses())) > 0:
            try:
                for item in root_class.subclasses():
                    self.__del_class_not_in_list(item, cut_class_list)
            except Exception as e:
                print(e)
        if root_class not in cut_class_list:
            try:
                destroy_entity(root_class)
            except Exception as e:
                print(e)

    # 创建新本体
    def __create_new_onto(self):
        return get_ontology(self.onto.base_iri)

    # 封装获取本体
    # 自动判断name和iri
    def __get_one_class(self, text):
        target_class = None
        if not self.onto.search_one(label=text) is None:
            print('label mathched')
            target_class = self.onto.search_one(label=text)
        if not self.onto.search_one(iri=text) is None:
            print('iri mathched')
            target_class = self.onto.search_one(iri=text)
        if not self.onto.search_one(id=text) is None:
            print('id mathched')
            target_class = self.onto.search_one(id=text)
        return target_class

    # 保存本体文件
    def save_new_onto(self, onto, add_flag=False):
        self.temp_class = []
        # 检查哪个方法调用
        if add_flag:
            print('add_owl_path')
            save_path = self.add_owl_path
        else:
            save_path = self.cut_save_path
        if save_path == '':
            save_path = "./new_onto.owl"
        onto.save(file=save_path, format='rdfxml')
        return save_path

    # 切割得到某一个术语下所有的数据
    def cut_part_onto(self, term):
        print(self.onto.base_iri)
        cut_root_class = self.__get_one_class(term)
        if cut_root_class is None:
            print("Class Information Not Found!")
            return

        self.temp_class = []
        self.__get_all_class(cut_root_class)  # 收集 {T} ∪ H
        S = set(self.temp_class)

        # 步骤1：移除不在 S 中的术语
        self.__del_class_not_in_list(Thing, S)

        # 步骤2 & 3：移除关系
        relationships = list(self.onto.object_properties())
        for r in relationships:
            subject = r.domain[0] if r.domain else None
            object = r.range[0] if r.range else None
            if subject not in S or object not in S:
                destroy_entity(r)

        # 保存修改后的本体
        save_path = self.save_new_onto(self.onto)
        return save_path

        # 切割得到某一术语下，某一术语之前所有数据

    def cut_part_onto_selection(self, begin_term, *end_terms):
        begin_class = self.__get_one_class(begin_term)
        if begin_class is None:
            print("Head Class Information Not Found!")
            return

        # 步骤1：获取 begin-term 的所有子节点
        self.temp_class = []
        self.__get_all_class(begin_class)
        all_subclasses = set(self.temp_class)
        all_subclasses.add(begin_class)

        # 步骤2：获取 end-term 的子节点
        end_subclasses = set()
        end_classes = []
        for end_term in end_terms:
            end_class = self.__get_one_class(end_term)
            if end_class is None:
                print(f"End Class {end_term} Not Found!")
                continue
            if end_class not in all_subclasses:
                print(f"Warning: {end_term} is not a subclass of {begin_term}")
                continue
            end_classes.append(end_class)
            self.temp_class = []
            self.__get_all_class(end_class)
            end_subclasses.update(self.temp_class)  # 仅子节点

        # 步骤3：删除 end-term 的子节点，保留 end-term 本身
        S = all_subclasses - end_subclasses
        S.update(end_classes)

        # 移除不在范围 S 中的类
        self.__del_class_not_in_list(Thing, S)

        # 移除不相关的关系
        relationships = list(self.onto.object_properties())
        for r in relationships:
            subject = r.domain[0] if r.domain else None
            object = r.range[0] if r.range else None
            if subject not in S or object not in S:
                destroy_entity(r)

        save_path = self.save_new_onto(self.onto)
        return save_path

    # 通过新建本体完成本体切割
    # 动态构建
    # todo: 暂时放弃
    def build_part_onto(self, term):
        print(self.onto.base_iri)
        build_root_class = self.onto.search_one(label=term)
        if build_root_class is None:
            print("Class Information Not Found!")
        # 需要在创建新本体之前，清除原加载本体的数据
        self.onto.destroy()
        self.onto = get_ontology(self.owl_path)
        # 获取该节点下所有的节点和结构，基于is_a结构
        new_onto = get_ontology(self.onto.base_iri)
        # new_onto.load()
        print(Thing)
        print(build_root_class.name)

        with new_onto:
            class Test(build_root_class):
                pass

            '''
            for item in build_root_class.subclasses():
                class_dest = types.new_class(item.name, (Thing,))
                for parent in list(item.is_a):
                    if not isinstance(parent, Thing): item.is_a.remove(parent)  # Bank node
                    class_dest.is_a.append(parent)
            '''
        self.save_new_onto(new_onto)

    # 获取类的所有子类（包括匿名子类，不包括废弃的类）
    # if hasattr(cls, "deprecated") and cls.deprecated:
    def __get_all_non_deprecated_subclasses(self, cls):
        '''
        all_subclasses = set(cls.subclasses())
        for subclass in cls.subclasses():
            #if hasattr(cls, "deprecated") and not cls.deprecated:
            if (hasattr(cls, "deprecated") and (not cls.deprecated)):
                all_subclasses |= self.get_all_subclasses(subclass)
        '''
        all_subclasses = []
        for subclass in cls.subclasses():
            if not hasattr(subclass, "deprecated") or not subclass.deprecated:
                all_subclasses.append(subclass)
                all_subclasses.extend(self.__get_all_non_deprecated_subclasses(subclass))
        return set(all_subclasses)

    def test(self):
        # self.Translate_ONTO_with_Qwen()
        # self.__owl_to_csv()
        # self.__add_Chinese_label('./final_curation.csv')
        # self.owl_to_json()
        self.__get_class_context(Thing, '')
        print(self.all_class_with_context)

    # 将术语的汉语翻译添加到本体中，最终将翻译后的数据保存到owl文件中
    # 需要将各个路径规整一下
    def add_Chinese_label(self, owl_path, trans_path):
        self.onto.destroy()
        self.onto = get_ontology(owl_path).load()
        # 获取翻译后的数据
        Chinese_label_data = read_csv(trans_path)
        # 获取翻译后的数据
        for _, item in Chinese_label_data.iterrows():
            if not isna(item['label_cn']):
                item_class = self.onto.search_one(iri=item[0])
                if item_class is not None:
                    item_class.label = [locstr(item[2], lang='en'), locstr(item[3], lang='zh')]
        # 保存本体
        save_path = self.save_new_onto(self.onto, add_flag=True)
        # 返回生成的本体
        return save_path

    # Update: add and save more language to local ontology
    # label_language: zh, fr, de
    def add_other_label(self, owl_path, trans_path, language_label):
        self.onto.destroy()
        self.onto = get_ontology(owl_path).load()
        label_language_list = ['zh', 'fr', 'de']
        if language_label not in label_language_list:
            raise ValueError("The translation label code should be in the following languages code: zh, fr, de")
        # 获取翻译后的数据
        label_data = read_csv(trans_path)
        # 获取翻译后的数据
        for _, item in label_data.iterrows():
            if not isna(item[3]):
                item_class = self.onto.search_one(iri=item[0])
                if item_class is not None:
                    item_class.label = [locstr(item[2], lang='en'), locstr(item[3], lang=language_label)]
        # 保存本体
        save_path = self.save_new_onto(self.onto, add_flag=True)
        # 返回生成的本体
        return save_path


    # 将本体文件中的所有数据输出到csv文件中
    def owl_to_csv(self, owl_path):
        save_path = self.owl2csv_path

        self.onto.destroy()
        self.onto = get_ontology(owl_path).load()
        # 获取Thing下所有子类
        subcls = self.__get_all_non_deprecated_subclasses(Thing)
        all_sub_cls = []
        # l_translate = TRANSLATE()
        for item in tqdm(subcls):
            all_sub_cls.append([item.iri, item.name, item.label[0]])
            # all_sub_cls.append([item.iri, item.name, item.label[0], l_translate.local_translate(item.label[0])])
        DataFrame(data=all_sub_cls, columns=['IRI', 'name', 'label_en']).to_csv(save_path, index=False,
                                                                                encoding='utf_8_sig')
        # DataFrame(data=all_sub_cls, columns=['IRI', 'name', 'label_en', 'machine translation']).to_csv(save_path, index=False, encoding='utf_8_sig')
        return all_sub_cls

    # 将本体文件按照上下文形式输出到csv文件中
    def owl_to_csv_with_context(self):
        self.__get_class_context(Thing, '')
        all_class_with_context = []
        for item in self.all_class_with_context:
            all_class_with_context.append([item.split('$$')[0].split('@')[-1], item.split('$$')[1]])
        DataFrame(all_class_with_context, columns=['IRI', 'term']).to_csv('整理/all_data_with_context.csv', index=False,
                                                                          encoding='utf_8_sig')
        self.all_class_with_context = []

    # 遍历owl文件，取得所有class的上下文
    def __get_class_context(self, cls, temp_term):
        print(cls.iri)
        # 选取英文label
        if hasattr(cls, 'label') and cls.label:
            # 如果有 label 属性，取第一个元素（如果有多个标签）
            cls_label = cls.label[0]
        else:
            # 如果没有 label 属性或者属性为空，使用类名作为标签
            cls_label = cls.name  # 或者你可以选择其他方式来处理没有标签的情况

        if cls_label != 'Thing':
            temp_term_list = temp_term.split('$$')
            if len(temp_term_list) > 1:
                temp_term = temp_term_list[0] + '@' + str(cls.iri) + '$$' + temp_term_list[1] + '@' + str(cls_label)
            else:
                temp_term = str(cls.iri) + '$$' + str(cls_label)
            self.all_class_with_context.append(temp_term)
        print(temp_term)
        for subclass in cls.subclasses():
            if not hasattr(subclass, "deprecated") or not subclass.deprecated:
                self.__get_class_context(subclass, temp_term)

    # 遍历owl文件，并取得所有的class和其关系
    def __get_entity_and_relation(self, cls):
        # 选取英文label
        if hasattr(cls, 'label') and cls.label:
            # 如果有 label 属性，取第一个元素（如果有多个标签）
            label = cls.label[0]
        else:
            # 如果没有 label 属性或者属性为空，使用类名作为标签
            label = cls.name  # 或者你可以选择其他方式来处理没有标签的情况
        self.entities.append(cls.name + '@@' + label)
        for subclass in cls.subclasses():
            if not hasattr(subclass, "deprecated") or not subclass.deprecated:
                self.relations.append(cls.name + '@@' + subclass.name)
                self.__get_entity_and_relation(subclass)

    # 将owl文件解析成D3.js适配文件
    def owl_to_json(self):
        # 1. 提取本体中的概念和关系
        self.entities = []
        self.relations = []
        entities = []
        relations = []

        # 2.获取本体所有数据
        self.__get_entity_and_relation(Thing)

        # 3. 将数据转化为d3.js适合的格式
        if len(self.entities) > 0:
            for item in self.entities:
                entities.append({'id': item.split('@@')[0], 'label': item.split('@@')[1]})

        if len(self.relations) > 0:
            for item in self.relations:
                relations.append({'source': item.split('@@')[0], 'target': item.split('@@')[1]})

        # 3. 将数据转换为 JSON
        data = {
            'entities': entities,
            'relations': relations
        }
        return data

    # 翻译本体数据
    # Python package翻译
    # 本地翻译，目前使用MIT协议的翻译包
    def translate_terms_with_Package(self, csv_path, translation_mode):
        trans = TRANSLATE(translation_mode)
        result = []
        data = read_csv(csv_path)
        # 收集所有数据
        all_items = []
        for _, item in tqdm(data.iterrows()):
            all_items.append([item['IRI'], item['name'], item['label_en']])
        # better display
        for item in tqdm(all_items):
            t = trans.local_translate(item[2])
            result.append([item[0], item[1], item[2], t])
        #DataFrame(result, columns=['IRI', 'name', 'label_en', 'label_cn']).to_csv(
        DataFrame(result, columns=['IRI', 'name', 'label_en', 'label_' + translation_mode]).to_csv(
            self.translate2csv_dir + 'all_classes_with_package.csv', index=False, encoding='utf_8_sig')

    # 使用GLM-130B翻译
    def translate_terms_with_GLM(self, csv_path, api_key, translation_mode, model_name="glm-4"):
        trans = TRANSLATE(translation_mode)
        result = []
        data = read_csv(csv_path)
        # 收集所有数据
        all_items = []
        for _, item in tqdm(data.iterrows()):
            all_items.append([item['IRI'], item['name'], item['label_en']])

        for item in tqdm(all_items):
            t = trans.glm_api(item[2], api_key=api_key, model_name=model_name)
            result.append([item[0], item[1], item[2], t])
        #DataFrame(result, columns=['IRI', 'name', 'label_en', 'label_cn']).to_csv(
        DataFrame(result, columns=['IRI', 'name', 'label_en', 'label_' + translation_mode]).to_csv(
            self.translate2csv_dir + 'all_classes_with_GLM.csv', index=False, encoding='utf_8_sig')

    # 使用Google Gemini 翻译，目前1.5Pro已公开，但是有访问限制
    def translate_terms_with_gemini(self, csv_path, api_key, translation_mode, model_name="gemini-1.5-flash"):
        trans = TRANSLATE(translation_mode)
        result = []
        data = read_csv(csv_path)
        # 收集所有数据
        all_items = []
        for _, item in tqdm(data.iterrows()):
            all_items.append([item['IRI'], item['name'], item['label_en']])
        for item in tqdm(all_items):
            t = trans.gemini_api(item[2], api_key=api_key, model_name=model_name)
            result.append([item[0], item[1], item[2], t])
        #DataFrame(result, columns=['IRI', 'name', 'label_en', 'label_cn']).to_csv(
        DataFrame(result, columns=['IRI', 'name', 'label_en', 'label_' + translation_mode]).to_csv(
            self.translate2csv_dir + 'all_classes_with_gemini.csv', index=False, encoding='utf_8_sig')

    # 使用deepl翻译，需要用户输入auth key
    def translate_terms_with_deepl(self, csv_path, translation_mode, auth_key):
        trans = TRANSLATE(translation_mode)
        result = []
        data = read_csv(csv_path)
        # 收集所有数据
        all_items = []
        for _, item in tqdm(data.iterrows()):
            all_items.append([item['IRI'], item['name'], item['label_en']])

        for item in tqdm(all_items):
            t = trans.deepl_api(item[2], auth_key=auth_key)
            result.append([item[0], item[1], item[2], t])
        #DataFrame(result, columns=['IRI', 'name', 'label_en', 'label_cn']).to_csv(
        DataFrame(result, columns=['IRI', 'name', 'label_en', 'label_' + translation_mode]).to_csv(
            self.translate2csv_dir + 'all_classes_with_deepl.csv',
            index=False, encoding='utf_8_sig')


class Process(object):
    def __init__(self):
        pass

    def begin_parser(self):
        description = 'Py2ONTO-Edit, a python-based tool for ontology term extraction and translation.'
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=description)
        parser.add_argument('-o', '--owl_path', required=True, type=str, help='local ontology path')
        parser.add_argument('-m', '--cut_method', required=True, type=str, choices=['all', 'select', 'none'],
                            default='none', help='entry all/select to deicide cut method')
        parser.add_argument('-c', '--cut_save_path', type=str, default='./result/cut_onto.owl',
                            help='cut ontology save path')
        # 用户自行搭配，指定-m为none时不进行切分，不指定-t的许可值不进行翻译
        # parser.add_argument('-m', '--method', required=True, type=str, help='entry c/t to assign cut or translation method')
        parser.add_argument('-s', '--single_root', type=str, help='root term for cutting')
        parser.add_argument('-e', '--end_nodes', type=str, help='tail terms for cutting, for example term1,term2,term3')
        parser.add_argument('-l', '--translation_mode', type=str, help='tranlate English term to other language', choices=['en2zh', 'en2fr', 'en2de'])
        parser.add_argument('-t', '--translation_methods', type=str, choices=['l', 'd', 'g', 'c'],
                            help='entry l/d/g/c to assign local/deepl/gemini/chatglm4')
        parser.add_argument('-p', '--owl2csv_path', type=str, default='./result/part_onto.csv', help='owl to csv path')
        parser.add_argument('-d', '--translate2csv_dir', type=str, default='./result/',
                            help='translate to csv dictionary')
        parser.add_argument('-a', '--add_translated_owl_path', type=str, default='./result/add2onto.owl',
                            help='translated csv path to owl file')
        return parser

    def run_parser(self, args):
        # 读取api key配置文件
        if os.path.exists('./translation_api_key_setting.yaml'):
            with open('./translation_api_key_setting.yaml') as f:
                config_data = yaml.safe_load(f)
        else:
            raise ValueError('Missing API keys configuration file')

        # 获取当前文件的路径
        current_path = os.path.dirname(os.path.abspath(__file__))
        print(current_path)
        # 检查目录是否存在
        if not os.path.exists(os.path.join(current_path, 'result')):
            # 创建result目录存储结果文件
            os.makedirs(os.path.join(current_path, 'result'))

        try:
            cutONTO = EDIT_ONTO(args.owl_path)
            cutONTO.cut_save_path = args.cut_save_path
            cutONTO.owl2csv_path = args.owl2csv_path
            cutONTO.translate2csv_dir = args.translate2csv_dir
            cutONTO.add_owl_path = args.add_translated_owl_path

            if args.cut_method == 'all':
                strat_root = args.single_root
                if strat_root:
                    print('Get data under a single node')
                    cutONTO.cut_part_onto(args.single_root)
                else:
                    raise ValueError('Missing a centain node to get the ontology before a single node')

            elif args.cut_method == 'select':
                strat_root = args.single_root
                # 将 end_nodes 参数拆分成一个列表, 按逗号分隔，中间不能有空格
                end_nodes = args.end_nodes.split(',') if args.end_nodes else []
                if strat_root and end_nodes:
                    print('Beginning extraction')
                    cutONTO.cut_part_onto_selection(strat_root, *end_nodes)
                elif strat_root:
                    print('Missing end nodes, get data under a single node')
                    cutONTO.cut_part_onto(args.single_root)
                else:
                    raise ValueError('Missing start node and end nodes')
            else:
                print('No cut method')

            if args.cut_method == 'all' or args.cut_method == 'select':
                print('Cutting ontology successfully')
                # 将切割好的本体或者原本体中所有数据导出为csv格式,存储为part_onto.csv
                cutONTO.owl_to_csv(cutONTO.cut_save_path)
            elif args.cut_method == 'none':
                cutONTO.owl_to_csv(args.owl_path)
            else:
                raise ValueError('Cutting ontology failed or missing owl path')

            # 设置翻译模式
            translation_mode = args.translation_mode
            if translation_mode == 'en2zh':
                language_label = 'zh'
            elif translation_mode == 'en2fr':
                language_label = 'fr'
            elif translation_mode == 'en2de':
                language_label = 'de'

            # 调用翻译函数
            translation_method = args.translation_methods
            if translation_method:
                if translation_method == 'l':
                    print("Using local translation method")
                    method = "package"
                    # 调用本地翻译方法
                    cutONTO.translate_terms_with_Package(cutONTO.owl2csv_path, translation_mode)
                elif translation_method == 'd':
                    print("Using Deepl translation method, Please fill in the key information in the code.")
                    method = "deepl"
                    # 检测是否配置了deepl的 auth_key
                    deepl_api = config_data['deepl_setting']['auth_key']
                    if len(deepl_api) <= 0:
                        raise ValueError("Missing API keys of DeepL")
                    else:
                        # 调用Deepl翻译方法
                        cutONTO.translate_terms_with_deepl(cutONTO.owl2csv_path, translation_mode,
                                                       auth_key=deepl_api)
                elif translation_method == 'g':
                    print("Using Gemini translation method, Please fill in the key information in the code.")
                    method = "gemini"
                    # 检测是否配备了gemini的 API key
                    gemini_api = config_data['gemini_setting']['api_key']
                    if len(gemini_api) <= 0:
                        raise ValueError("Missing API keys of gemini")
                    else:
                        # 调用Gemini翻译方法
                        cutONTO.translate_terms_with_gemini(cutONTO.owl2csv_path, gemini_api, translation_mode)
                elif translation_method == 'c':
                    print("Using ChatGLM4 translation method, Please fill in the key information in the code.")
                    method = "GLM"
                    # 检测是否配备了GLM4 API Key
                    glm_api = config_data['glm_setting']['api_key']
                    if len(glm_api) <= 0:
                        raise ValueError("Missing API keys of glm")
                    else:
                        # 调用ChatGLM4翻译方法
                        cutONTO.translate_terms_with_GLM(cutONTO.owl2csv_path, glm_api, translation_mode)
                else:
                    raise ValueError("Invalid translation method")

                # 将翻译好的数据保存到本体中
                translate_file = os.path.join(cutONTO.translate2csv_dir, './all_classes_with_' + method + '.csv')
                if os.path.exists(translate_file):
                    if args.cut_method == 'all' or args.cut_method == 'select':
                        #cutONTO.add_Chinese_label(cutONTO.cut_save_path, translate_file)
                        cutONTO.add_other_label(cutONTO.cut_save_path, translate_file, language_label)
                    else:
                        #cutONTO.add_Chinese_label(args.owl_path, translate_file)
                        cutONTO.add_other_label(args.owl_path, translate_file, language_label)

                    print('Translation add to ontology successful')
                else:
                    raise ValueError('Translation failed or missing csv path')

        except Exception as e:
            print('Error: ', e)


if __name__ == '__main__':
    p = Process()
    parser = p.begin_parser()
    args = parser.parse_args()
    p.run_parser(args)
