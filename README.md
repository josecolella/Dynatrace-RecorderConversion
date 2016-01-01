# Dynatrace-RecorderConversion

A Python 3 commandline program to convert from json to gsl for Dynatrace Recorder.
The Dynatrace Recorder reads two types of files; json and gsl, that denote the steps
to a particular test. This includes the browser agent, steps, and corresponding actions to a test.

##Purpose

The purpose was made for automation purposes. If a user wants to write the test using json and
have it converted to gsl which is the only format that can be saved remotely.

##How to use

```sh
# The -o option is optional
python3 main.py -i input.json -o output.gsl
# If no -o option is used, a tmp.gsl
python3 main.py -i input.json
```

##Dependencies

```sh
pip install lxml
```


##Road map

- ~~Program must convert json to gsl~~
- Write tests to validate the conversion
- Program must convert gsl to json
- Write tests to validate the conversion
