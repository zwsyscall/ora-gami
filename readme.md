# ora-gami

This is a simple Python script intended to parse `.ora` files in order to extract each layer with the appropriate filename.

## Overview

This extracts individual image layers from an `.ora` (OpenRaster) file by unzipping the file, parsing the embedded XML file, and copying the layer images to a specified output folder. Optionally, it can also translate the layer filenames using Google Translate.


### Command-line Options

- `-t`, `--translate`  
  Enable translation of layer filenames (note: this may be slow due to API response times).

- `-s`, `--source`  
  Specify the source language for translation (default is `ja` for Japanese).

- `-d`, `--dest`  
  Specify the destination language for translation (default is `en` for English).

- `-D`, `--destination-folder`  
  Specify the folder where the extracted layer files will be saved. If not provided, a default folder will be created based on the input filename.

- `-v`, `--verbose`  
  Enable verbose output for detailed logging.

#### Example

Extract layers from an `.ora` file with translation enabled:

```bash
python ora-gami.py -t -s ja -d en -D output_layers some_texture.ora
```
