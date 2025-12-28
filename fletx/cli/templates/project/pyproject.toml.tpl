[project]
name = "{{ name }}"
version = "{{ version }}"
description = "{{ description }}"
readme = "README.md"
authors = [{ name = "{{ author }}", email = "" }]
requires-python = ">={{ python_version }}"
dependencies = [
    "fletxr=={{ fletx_version }}",
    "flet[all]==0.28.3",
]