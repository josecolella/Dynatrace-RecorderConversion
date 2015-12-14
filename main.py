import argparse
from DynatraceRecorderConverter import DynatraceRecorderConverter

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Dynatrace Recorder Converter")
    parser.add_argument(
        "-i", "--input", help="The name of the input file", type=str, required=True)
    parser.add_argument(
        "-o", "--output", help="The name of the output file", type=str, default="tmp")
    parser.add_argument(
        "-v", "--verbose", help="Display debug message", action="store_true")
    args = parser.parse_args()
    DynatraceRecorderConverter.convertJSONFileToGSLFile(
        args.input, args.output)
