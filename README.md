![image](https://github.com/user-attachments/assets/79c2af59-4ae8-48ad-8ba5-dac9f01f4eba)![image](https://github.com/user-attachments/assets/c9b0bb3a-ae35-4059-b26d-0db932d3bae1)# Py2ONTO-Edit

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
- [Usage](#Usage)
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

* Local translation functions require downloading the local Argos-Translate model. The model file must be downloaded into the models folder in this project.
```
- en_zh.argosmodel
- translate-en_zh-1_1
weblink: https://drive.google.com/drive/folders/11wxM3Ze7NCgOk_tdtRjwet10DmtvFu3i

or in Argos Official web page
weblink: https://www.argosopentech.com/argospm/index/
```

### Usage
There are two use-case in our project, please visit **Usage-FOLDER**
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
humanDO.translate_terms_with_deepl("./part_onto.csv",'your-deepl-api')

# 2.3 Saving translated label data to the ontology
humanDO.add_Chinese_label('./new_onto.owl', './all_classes_with_deepl.csv')
```

#### Usage of PyONTO-Edit in command-line interface (CLI)
```
Task 1: only segment ontology
python editonto.py -o ./HumanDO.owl -m all -s “orofacial cleft”
```

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

