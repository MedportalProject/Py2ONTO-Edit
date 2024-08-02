# Py2ONTO-Edit

Py2ONTO-Edit: A Python-based Tool for Ontology Segmentation and Terms Translation
<a href="https://github.com/MedportalProject/Py2ONTO-Edit">
  <img src="https://github.com/MedportalProject/Py2ONTO-Edit/blob/main/figs/logo-edit.png" alt="Logo">
</a>
<h1 align="center">
  <a href="">
    <img src="https://img.shields.io/badge/releases-v0.2-red" />
  </a>
  <a href="">
    <img src="https://img.shields.io/badge/docs-v1.0-yellow" />
  </a>
  <a href="">
    <img src="https://img.shields.io/badge/Ontology-Tools-blue" />
  </a>
  <a href="">
    <img src="https://img.shields.io/badge/LICENSE-GPL 3-brightgreen" />
  </a>
</h1>

## Catalogue
- [Introduction](#Introduction)
- [Update](#Update)
- [Filetree](#Filetree)
- [Getting_Started](#Getting_Started)
- [Cite](#Cite)

### Introduction
Py2ONTO-Edit updates new functions that fouces on ontology segmentation and term translation of Python-Project

### Update
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
Requirements:
```
Python >= 3.10
```
Package dependency:
```
# Py2ONTO-Edit supports running in CLI and code 
pip install -r requirement.txt
```
There are two use-case in our project, please visit FOLDER-**Usage**

* Local translation functions require to download the local Argos-Translate model.
```
- en_zh.argosmodel
- translate-en_zh-1_1
weblink: https://drive.google.com/drive/folders/11wxM3Ze7NCgOk_tdtRjwet10DmtvFu3i

or in Argos Official web page
weblink: https://www.argosopentech.com/argospm/index/
```
It is required to download the model file into the models folder in this project.


### Cite
If you find our work useful for your research, please consider citing it:
```
@article{wang2024XXXX,
  title={Py2ONTO V0.2: a Python-based Tool for Ontology Segmentation and Terms Translation},
  author={Zhe Wang, Zhigang Wang, Zunfan Chen, Shen Yang, Xiaolin Yang1 and Yan Zhu},
  journal={XXXXX},
  year={2024}
- todo
```

