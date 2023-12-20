# Code Detection Python Library
The Code Detection Python library provides convenient access to the Code Detection API from applications written in Python language. It includes a pre-defined set of classes for API resources that initialize themselves dynamically from API responses which makes it compatible with the Code Detection API.

## Documentation
See the [Code Detection API documentation](https://platform.runtime.dev/)

## Installation
You don't need this source code unless you want to modify the package. If you just want to use the package, just run:
```shell
pip install codedetectionapi
```

## Usage
The library needs to be configured with your account's API key which is available on the [website](https://console.runtime.dev/#/portal). Set it as the CODEDETECTION_API_KEY environment variable before using the library:
```shell
export CODEDETECTION_API_KEY=<your-api-key>
```
Or set ```codedetection.api_key``` to its value (not recommended):
```python
import codedetection

codedetection.api_key = "<your-api-key>"
```

## Example code
### Programming language classification
```python
import codedetection

response = codedetection.Classifier.classify(['std::cout << "Hello World";'])[0]["language"] # cpp
```
An example of how to call the Classifier method is shown in the [get programming language notebook](https://github.com/open-runtime/Code-Detection-API/blob/main/examples/classifier.ipynb).

### Code vs Text evaluation
```python
import codedetection

response = codedetection.CodeVsText.evaluate(['std::cout << "Hello World";'])[0]["naturalLanguage"] # False
```
An example of how to call the CodeVsText method is shown in the [evaluate code vs text notebook](https://github.com/open-runtime/Code-Detection-API/blob/main/examples/codevstext.ipynb).

### Tokenization
```python
import codedetection

response = codedetection.Tokenizer.tokenize(['std::cout << "Hello World";'])[0]["tokens"] # [799.0, 173.0, 4003.0, ...]
```
An example of how to call the CodeVsText method is shown in the [tokenize string notebook](https://github.com/open-runtime/Code-Detection-API/blob/main/examples/tokenizer.ipynb).

### Overall string data
```python
import codedetection

response = codedetection.TLP.create(['std::cout << "Hello World";'])
```
An example of how to call the TLP method is shown in the [get string data notebook](https://github.com/open-runtime/Code-Detection-API/blob/main/examples/tlp.ipynb).
