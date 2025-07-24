<a href="https://github.com/MedportalProject/Py2ONTO-Edit">
  <img src="https://github.com/MedportalProject/Py2ONTO-Edit/blob/main/figs/logo-edit2.png" alt="Logo">
</a>

# Py2ONTO-Edit

A Python-based Tool for Term Extraction and Translation of Ontology
<h1 align="center">
  <a href="">
    <img src="https://img.shields.io/badge/releases-v1.0-red" />
  </a>
  <a href="">
    <img src="https://img.shields.io/badge/docs-v1.0-yellow" />
  </a>
  <a href="">
    <img src="https://img.shields.io/badge/Ontology-Tools-blue" />
  </a>
  <a href="">
    <img src="https://img.shields.io/badge/LICENSE-LGPL 3-brightgreen" />
  </a>
  <a href="">
    <img src="https://img.shields.io/badge/Python-snow?logo=python&logoColor=3776AB" alt="" />
  </a>
</h1>

## Catalogue
- [Introduction](#Introduction)
- [Update](#Update)
- [Filetree](#Filetree)
- [Getting_Started](#Getting_Started)
- [Usage](#Usage)
- [Cite](#Cite)

### Introduction
Py2ONTO-Edit updates new functions that fouces on term extraction and translation of Python-Project

### Update
[2025/7/24]
- Updated extract method
- Fixed some bugs

[2025/7/6]
- Fixed some bugs

[2024/8/6]
- Add new translate function
- Support for translation from English to German
- Support for translation from English to French

[2024/8/2]Release Py2ONTO-EDIT
- Initialisation project

### Filetree 
```
filetree 
├── ARCHITECTURE.md
├── LICENSE
├── editonto.py
├── /models/
│  ├── en_zh.argosmodel
│  ├── translate-en_zh-1_1.argosmodel
│  └── translate-en_zh-1_9.argosmodel
├── /Usage/
│  ├── /example-result/
│  │  ├── /Example in CLI-Result/
│  │  └── /Example in code-Result/
│  │  └── readme.md
│  │  └── Example in CLI.ipynb
│  │  └── Example in code.ipynb
│  │  └── HumanDO.owl
│  │  └── translation_api_key_setting.yaml
├── requirement.txt
├── translation_api_key_setting.yaml
└── README.md
```

### Getting_Started
**Requirements:**
```
Python >= 3.10
```

**Package dependency:**
```
# Py2ONTO-Edit supports running in CLI and code 
pip install -r requirement.txt
```
> [!NOTE]
> * Local translation functions require downloading the local Argos-Translate model. The model file must be downloaded into the models folder in this project.
```
English to Chinese, French and German      
- en_zh.argosmodel
- translate-en_zh-1_1.argosmodel
- translate-en_zh-1_9.argosmodel(en2zh:suggestion)  
- translate-en_de-1_5.argosmodel(en2de:suggestion)  
- en_fr.argosmodel(en2fr:suggestion)     
weblink: https://drive.google.com/drive/folders/11wxM3Ze7NCgOk_tdtRjwet10DmtvFu3i

or in Argos Official web page
- translate-en_zh-1_9.argosmodel(en2zh:suggestion)  
- translate-en_fr-1_9.argosmodel(en2fr:suggestion)
- translate-en_de-1_0.argosmodel(en2de:suggestion)  
weblink: https://www.argosopentech.com/argospm/index/
```
> [!NOTE]
> **You must enter your DeepL auth key, ChatGLM-130B auth key, and Gemini auth key in the file _'translation_api_key_setting.yaml'_ to translate terms via Py2ONTO-Edit.**

### Usage
There are two use-case in our project, please visit **Usage-FOLDER**    
- [Example in CLI.ipynb](https://github.com/MedportalProject/Py2ONTO-Edit/blob/main/Usage/Example%20in%20CLI.ipynb)   
- [Example in code.ipynb](https://github.com/MedportalProject/Py2ONTO-Edit/blob/main/Usage/Example%20in%20code.ipynb)    

#### Usage of PyONTO-Edit in programming environment (Python)
```
# import all function of py2onto-edit
from editonto import *
# load HumanDO.owl
humanDO = EDIT_ONTO("./HumanDO.owl")

# 1.1 Segmentation method 1: Global extraction method
# Get all data under a single root node and store to new_onto.owl
humanDO.cut_part_onto('orofacial cleft')

# 2.1 Export all class data from ontology into csv file
humanDO.owl_to_csv("./new_onto.owl")

# 2.2 Translation with DeepL
humanDO.translate_terms_with_deepl("./part_onto.csv", "en2zh", "your-deepl-api")

# 2.3 Saving translated label data to the ontology
# zh:Chinese label; fr:French label; de:German label
humanDO.add_Chinese_label('./new_onto.owl', './all_classes_with_deepl.csv', 'zh')
```

#### Usage of PyONTO-Edit in command-line interface (CLI)
```
# help of Py2ONTO-Edit
python editonto.py -h
```

Task 1: only terms extraction (global extraction)
```
python editonto.py -o ./HumanDO.owl -m all -s "orofacial cleft"
```

Task 2: only terms extraction (selective depth extraction)

*use EFO ontology
```
python editonto.py -o ./efo.owl -m select -s "cell type" -e "endothelial cell,kidney cell,stem cell"
```

Task 3: only terms translation
```
python editonto.py -o ./result/cut_onto.owl -m none -l "en2de" -t d  
```
> [!Note]
> -l: translation mode select  
> en2zh: English to Chinese  
> en2fr: English to French  
> en2de: English to German

> -t: translation server select   
> d: DeepL  
> l: argos translate  
> g: gemini  
> c: chatglm4

Task 4: extraction and translation of ontology terms
```
python editonto.py -o ./HumanDO.owl -m all -s "orofacial cleft" -l "en2zh" -t d  
```

### Cite
If you find our work useful for your research, please consider citing it:
```
@misc{wang2024py2onto-edit,
author = {Zhe Wang, Zhigang Wang, Zunfan Chen, Shen Yang, Xiaolin Yang and Yan Zhu},
title={Py2ONTO-Edit: a Python-based Tool for Ontology Term Extraction and Translation},
year = {2024},
publisher = {GitHub},
howpublished = {\url{https://github.com/MedportalProject/Py2ONTO-Edit}},
note = {2024/08/01}
}
```

