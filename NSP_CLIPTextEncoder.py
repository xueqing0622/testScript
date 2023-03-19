import torch, os, json, random, hashlib
from urllib.request import urlopen
import json

class WAS_NSP_CLIPTextEncoder:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
                    "required": {
                            "noodle_key": ("STRING", {"default": '__', "multiline": False}),
                            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                            "text": ("STRING", {"multiline": True}),
                            "clip": ("CLIP",),
                    }
                }
        
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "nsp_encode"

    CATEGORY = "conditioning"

    def nsp_encode(self, clip, text, noodle_key='__', seed=0):
    
        # Fetch the NSP Pantry
        local_pantry = 'ComfyUI/custom_nodes/nsp_pantry.json'
        if not os.path.exists(local_pantry):
            response = urlopen('https://raw.githubusercontent.com/WASasquatch/noodle-soup-prompts/main/nsp_pantry.json')
            tmp_pantry = json.loads(response.read())
            # Dump JSON locally
            pantry_serialized = json.dumps(tmp_pantry, indent=4)
            with open(local_pantry, "w") as f:
                f.write(pantry_serialized)
            del response, tmp_pantry
        
        # Load local pantry
        with open(local_pantry, 'r') as f:
            nspterminology = json.load(f)
            
        if seed > 0 or seed < 1:
            random.seed(seed)
            
        # Parse Text
        new_text = text
        for term in nspterminology:
            # Target Noodle
            tkey = f'{noodle_key}{term}{noodle_key}'
            # How many occurances?
            tcount = new_text.count(tkey)
            # Apply random results for each noodle counted
            for _ in range(tcount):
                new_text = new_text.replace(tkey, random.choice(nspterminology[term]), 1)
                seed += 1
                random.seed(seed)
                
        print('Parsed Prompt:', new_text)

        output_dir = 'D:/ComfyUI_windows_portable/ComfyUI/output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Check if file with same name exists, if yes then add a number suffix to the filename
        index = 0
        while os.path.isfile(os.path.join(output_dir, f"new_text{index}.txt")):
            index += 1

        # Write to file
        filename = f"new_text{index}.txt"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(new_text)
        
        return ([[clip.encode(new_text), {}]], )

NODE_CLASS_MAPPINGS = {
    "CLIPTextEncode (NSP)": WAS_NSP_CLIPTextEncoder
}
