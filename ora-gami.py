from googletrans import Translator
import xmltodict
import threading
import argparse
import tempfile
import zipfile
import shutil
import os

def vprint(verbose, *args):
    if verbose:
        print(*args)

def parse_args():
    parser = argparse.ArgumentParser(description="Export layers with the appropriate filenames from .ora files")
    parser.add_argument(
        "--translate",
        "-t",
        action="store_true",
        default=False,
        help="Translate filenames, you might get ratelimited by Google.",
    )
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        default="ja",
        help="Source language for translation (default: Japanese).",
    )
    parser.add_argument(
        "--dest",
        "-d",
        type=str,
        default="en",
        help="Destination language for translation (default: English).",
    )
    parser.add_argument(
        "--destination-folder",
        "-D",
        type=str,
        help="Folder to write the layer files.",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output.",
    )

    parser.add_argument(
        "filename",
        help="List of file paths to process.",
    )

    return parser.parse_args()

def move_file(layer_dictionary, src, dest, translator, src_lang: str, dest_lang: str):
    image_file_path = os.path.join(src, layer_dictionary["@src"])
    if translator is not None:
        image_name = translate_file(translator, src_lang, dest_lang, layer_dictionary["@name"]).text
    else:
        image_name = layer_dictionary["@name"]

    image_output_path = os.path.join(dest, f"{image_name}.png")
    shutil.copy(image_file_path, image_output_path)


def translate_file(translator, src_lang: str, dest_lang: str, text: str) -> str:
    return translator.translate(text, src=src_lang, dest=dest_lang)

def parse_stack_file(file_path: str, verbosity: bool):
    if not os.path.isfile(file_path):
        raise FileNotFoundError("Stack XML File does not exist!")
    vprint(verbosity, f"[+] Parsing XML file {file_path}")
    xml_handle = open(file_path, "r")

    with open(file_path, "r", encoding="utf-8") as xml_handle:
        return xmltodict.parse(xml_handle.read())



def parse_file(file_path, destination_path, verbosity, translator, src_lang, dest_lang):
    if not os.path.isfile(file_path):
        raise FileNotFoundError("Passed ora file does not exist!")
    
    with tempfile.TemporaryDirectory() as temp_path:
        vprint(verbosity, f"[+] Extracting {file_path} to a temporary directory {temp_path}")
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(temp_path)
        vprint(verbosity, "[+] Extracted files: ", os.listdir(temp_path))
        
        stack_file = os.path.join(temp_path, "stack.xml")
        stack_dictionary = parse_stack_file(stack_file, verbosity)
        
        vprint(verbosity, f"[+] Creating output folder {destination_path}")
        os.makedirs(destination_path, exist_ok=True)

    # I feel like this will cause issues later on but whatever
        try:
            threads = []
            def process_stack(item):
                if isinstance(item, dict):
                    if "layer" in item:
                        layers = item["layer"]
                        if isinstance(layers, list):
                            for layer in layers:
                                thread = threading.Thread(
                                    target=move_file, 
                                    args=(layer, temp_path, destination_path, translator, src_lang, dest_lang)
                                )
                                thread.start()
                                threads.append(thread)
                        else:
                            thread = threading.Thread(
                                target=move_file, 
                                args=(layers, temp_path, destination_path, translator, src_lang, dest_lang)
                            )
                            thread.start()
                            threads.append(thread)
                    if "stack" in item:
                        process_stack(item["stack"])
                elif isinstance(item, list):
                    for sub_item in item:
                        process_stack(sub_item)
            process_stack(stack_dictionary["image"]["stack"])

        except Exception:
            raise ValueError("Incorrect stack file configuration. Please check the passed ora file.")


        for thread in threads:
            thread.join()
        vprint(verbosity, "[+] Cleaning up temporary files")

def main(args):
    if args.translate:
        translator = Translator()
    try:
        parse_file(
            args.filename,
            args.destination_folder if args.destination_folder else f"{os.path.splitext(args.filename)[0]}_layers",
            args.verbose,
            translator if args.translate else None,
            args.source,
            args.dest
        )
    except Exception as e:
        print(f"[!] {e}")

if __name__ == '__main__':
    args = parse_args()
    main(args)