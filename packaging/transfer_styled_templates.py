#!/usr/bin/env python3

import os
import os.path
import shutil

print("Copying the dynamic templates from docs to the web application")
source_templates = '../docs/_build/astutus_dynamic_templates'
print(f"source_templates: {source_templates}")
templates_dirpath = '../src/astutus/web/templates'

for dirpath, dirnames, filenames in os.walk(source_templates):
    for filename in filenames:
        input_path = os.path.join(dirpath, filename)
        print(f"input_path: {input_path}")
        relative_path = os.path.relpath(input_path, source_templates)
        print(f"relative_path: {relative_path}")
        output_path = os.path.join(templates_dirpath, relative_path)
        print(f"output_path: {output_path}")
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        shutil.copy(input_path, output_path)
        print()
