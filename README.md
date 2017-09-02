## Apache Log Formatter

### Dependencies
- python 3.6
- pandas

_For testing_
- Nose
- Mock

### Assumptions

Apache access log in the following format:
```
10.0.36.25 - - [31/Oct/1994:23:59:30 +0000] "GET /system/search.php HTTP/1.1" 200 1865
```
The defaults will take an `apache_httpd.log` and produce an `apache_httpd.msg` dataframe. If using another naming method, the dataframe will replace `.log` with `.msg` if possible. Please ensure you pass the `-df` flag and specify the custom name of the dataframe when running reports.

### Usage

Feed a log file to `parse_log_file.py` and a dataframe will be generated in msgpack format. This allows a workable format to be used for quick reporting via `run_report.py`.

**The argument `--help` can be passed for a detailed usage on both files.**

Sample of default parsing

```
python parse_log_file.py apache_httpd.log
```

Chunking is optional and defaulted to 2000 lines

```
python parse_log_file.py apache_httpd.log --chunk 500
```

Run a full report

```
python run_report.py -f
```

Use a custom named dataframe and output to txt file. Output will be found in `apache_httpd_results.txt`
```
python run_report.py -f -df apache_httpd_2017-01-01.msg --output txt
```

Run a report on top 10 unsuccessful requests and get the % unsuccessful
```
python run_report.py --top unsuccessful -u
```

Run a detailed report on the top 10 ip addresses and the top 5 page requests
```
python run_report.py --detailed_ips
```

Run unit tests
```
nosetests -s tests/unit_tests.py
```
