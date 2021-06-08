
# Meta Getter
A quick and dirty tool for classifying document data for a Medium article

## TODO
 - [ ] Resolve S3 file access issue
 - [ ] Upload file to S3 bucket (hardcoded)
 - [ ] Read file using `aws textract` command
 - [ ] (optional) Remove file from S3
 - [ ] update README.md

### Baseline commands for AWS s3 and textract
```bash
s3 cp <source> s3://<bucket>
aws textract detect-document-text \
    --document '{"S3Object": {"Bucket": "<bucket>", "Name": "<filename>"}'
aws s3 rm s3://<bucket>/<filename>
```

## Setup
```bash
# Clone this repository
git clone https://github.com/ydkadri/meta-getter.git

# Install requirements
cd meta-getter/
python3 -m pip install -r requirements.txt

# Optionally make the script directly executable from the CLI
chmod u+x quick_check.py
```


## Usage
The `meta-getter` uses [Apache Tika](https://tika.apache.org/) and [AWS Comprehend](https://aws.amazon.com/comprehend/) to identify if a document contains entities such as __NAME__ or __ADDRESS__. To allow the program to be called directly from the CLI, the Python `click` library was used.

```bash
python quick_check.py <filename>
```

## Outputs
The `quick_check` tool will output a JSON object containing basic file meta data, as well as information on the different classes of entity identified by the `aws comprehend detect-entities` call. This JSON can optionally be formatted for human readability using the `--pretty` flag.

Whilst this output is very basic, it would be trivial to pipe this to a data store to build up a repository of scanned files.

## A note on simplicity
This was designed to be a quick and dirty example of how easily this data can be extracted from a document or document set. In no way should this be considered a serious solution to the problem of PII detection in documents.
