"""
Uses a dataframe (msgpack) to generate custom reports.

Author: Thomas Johns @t0mj
"""
import argparse
import pandas as pd
import textwrap


class ReportRunner(object):
    def __init__(self, args=[], run_now=False):
        self.output = []
        if run_now:
            self.dataframe_file = args['dataframe_file']
            self.df = self.get_df()
            self.run_reports(**args)

    def run_reports(self, full, top, success_percent, unsuccess_percent, detailed_ips,
                    dataframe_file, return_type):
        if full or top:
            if full or top == 'requests':
                self.top_10_requests()
            if full or top == 'unsuccessful':
                self.top_10_unsuccessful_requests()
            if full or top == 'ips':
                self.top_10_ips()
        if full or success_percent:
            self.successful_requests()
        if full or unsuccess_percent:
            self.unsuccessful_requests()
        if full or detailed_ips:
            self.top_10_ips_detailed()
        if return_type == 'txt':
            f = open('apache_httpd_results.txt', 'w')
            for line in self.output:
                f.write(line + '\n')
        else:
            for line in self.output:
                print(line)
        print('\nReport completed.')

    def get_df(self):
        list_of_dfs = pd.read_msgpack(self.dataframe_file)
        # This checks if there is no list of DF's in the msg from only 1 chunk
        if isinstance(list_of_dfs, list):
            df = pd.concat(list_of_dfs)
        else:
            df = list_of_dfs
        return df

    def top_10_requests(self):
        self.output.append("\nTop 10 requests:")
        series = self.df['resource']
        series = series.str.split('?').str[0]
        self.output.append('\nResource\t\tNumber of requests')
        self.output.append('\n' + series.value_counts()[:10].to_string())

    def successful_requests(self):
        query_df = self.df.query('status >= 200 & status <= 300')
        percent_success = len(query_df)/len(self.df)
        self.output.append("\nPercentage of successful requests:")
        self.output.append("\n{:.2%}".format(percent_success))

    def unsuccessful_requests(self):
        query_df = self.df.query('status < 200 | status > 300')
        percent_success = len(query_df)/len(self.df)
        self.output.append("\nPercentage of successful requests:")
        self.output.append("\n{:.2%}".format(percent_success))

    def top_10_unsuccessful_requests(self):
        self.output.append("\nTop 10 unsuccessful requests:")
        query_df = self.df.query('status < 200 | status > 300')
        series = query_df['resource']
        series = series.str.split('?').str[0]
        self.output.append('\nResource\t\tNumber of Requests')
        self.output.append('\n' + series.value_counts()[:10].to_string())

    def top_10_ips(self):
        self.output.append("\nTop 10 ips")
        self.output.append('\nIP\t\tNumber of Requests')
        self.output.append('\n' + self.df['ip'].value_counts()[:10].to_string())

    def top_10_ips_detailed(self):
        self.output.append("\nTop 10 ip requests and detailed resources:")
        top_10_series = self.df['ip'].value_counts()[:10]
        for ip, requests in top_10_series.iteritems():
            self.output.append(f"\nTop 5 Requests for: {ip}")
            ip_df = self.df.query(f'ip == "{ip}"')
            ip_series = ip_df['resource']
            ip_series = ip_series.str.split('?').str[0]
            self.output.append('\n' + ip_series.value_counts()[:5].to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description=textwrap.dedent('''\
                                     Generates a report based on an apache_httpd dataframe.
                                     By default searches for an apache_httpd.msg dataframe.'''))
    parser.add_argument('-f', '--full', action='store_true', default=False,
                        help='Runs every report.')
    parser.add_argument('--top', choices=['requests', 'unsuccessful', 'ips'],
                        help=textwrap.dedent('''\
                        Top 10 report for
                        requests:\tRequests by resource and request amount
                        unsuccessful:\tRequests without a response between 200-300 by resource and request amount
                        ips:\t\tip addresses and number of requests
                        '''))
    parser.add_argument('-s', '--successful', dest='success_percent', action='store_true',
                        help='Percentage of successful requests.')
    parser.add_argument('-u', '--unsuccessful', dest='unsuccess_percent', action='store_true',
                        help='Percentage of unsuccessful requests.')
    parser.add_argument('--detailed_ips', action='store_true',
                        help='Detailed view of the top 10 ip addresses, number of requests, and top 5 pages requested.')
    parser.add_argument('-df', '--dataframe', dest='dataframe_file', default='apache_httpd.msg',
                        help='The location of the dataframe to run the report against. Default: apache_httpd.msg')
    parser.add_argument('--output', dest='return_type', choices=['cli', 'txt'], default='cli',
                        help='Return output via CLI (default) or in a txt file.')
    args = vars(parser.parse_args())
    if not any(args.values()):
        parser.error('No arguments provided.')

    ReportRunner(args, run_now=True)
