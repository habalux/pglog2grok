#!/usr/bin/env python
#
# Small script for generating a logstash grok filter and patterns for postgresql
# using a non-default log_line_prefix setting.
#
# Output of this script has NOT been tested in any production environment as of yet.
#
# Copyright (c) 2014, Teemu Haapoja <teemu.haapoja@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.


# Custom patterns
# PGLOG_TZ is a modified TZ pattern (original didn't recognize "EET" as valid)
pg_patterns = """
PGLOG_TZ (?:[PMCE][SDE]T|UTC)
PGLOG_APPLICATION_NAME .*?
PGLOG_USER_NAME .*?
PGLOG_DATABASE_NAME .*?
PGLOG_REMOTE_HOST_PORT (\[local\]|%{IP:host}\(%{POSINT:port}\))
PGLOG_REMOTE_HOST (\[local\]|%{IP:host})
PGLOG_PROCESS_ID %{POSINT}
PGLOG_TIMESTAMP %{TIMESTAMP_ISO8601} %{PGLOG_TZ:TZ}
PGLOG_COMMAND_TAG .*?
PGLOG_SQL_STATE .*?
PGLOG_SESSION_ID [0-9\.A-Fa-f]+
PGLOG_SESSION_LINE_NUMBER %{POSINT}
PGLOG_SESSION_START_TIMESTAMP %{PGLOG_TIMESTAMP}
PGLOG_VIRTUAL_TRANSACTION_ID ([\/0-9A-Fa-f]+)
PGLOG_TRANSACTION_ID ([0-9A-Fa-f])+
PGLOG_LOGLEVEL (DEBUG[1-5]|INFO|NOTICE|WARNING|ERROR|LOG|FATAL|PANIC|DETAIL)
PGLOG_MESSAGE .*
"""

def prefix_to_grok(pr):
	replace_map = {
		r'%a'	:	"%{PGLOG_APPLICATION_NAME:application_name}",
		r'%u'	:	"%{PGLOG_USER_NAME:user_name}",
		r'%d'	:	"%{PGLOG_DATABASE_NAME:database_name}",
		r'%r'	:	"%{PGLOG_REMOTE_HOST_PORT:remote_host_port}",
		r'%h'	:	"%{PGLOG_REMOTE_HOST:remote_host}",
		r'%p'	:	"%{PGLOG_PROCESS_ID:process_id}",
		r'%t'	:	"%{PGLOG_TIMESTAMP}",
		r'%m'	:	"%{PGLOG_TIMESTAMP}",
		r'%i'	:	"%{PGLOG_COMMAND_TAG:command_tag}",
		r'%e'	:	"%{PGLOG_SQL_STATE:sql_state}",
		r'%c'	:	"%{PGLOG_SESSION_ID:session_id}",
		r'%l'	:	"%{PGLOG_SESSION_LINE_NUMBER:session_line_number}",
		r'%s'	:	"%{PGLOG_SESSION_START_TIMESTAMP:session_start_timestamp}",
		r'%v'	:	"%{PGLOG_VIRTUAL_TRANSACTION_ID:virtual_transaction_id}",
		r'%x'	:	"%{PGLOG_TRANSACTION_ID:transaction_id}",
		r'%q'	:	"",

	}

	pr = pr.replace(r'%%',r'%')

	for k,v in replace_map.items():
		pr = pr.replace(k,v)

	return "%s%%{PGLOG_LOGLEVEL:loglevel}: %%{PGLOG_MESSAGE:message}"%(pr)

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description="Create a grok pattern for your postgresql configuration")
	parser.add_argument('-q','--quiet', help="Be quiet, only output the grok pattern", action='store_const', const=True)
	parser.add_argument('-p', '--prefix', help="log_line_prefix from YOUR postgresql.conf", required=True)
	
	args = parser.parse_args()

	if args.quiet:
		print prefix_to_grok(args.prefix)
	else:
		print "You need to add these patterns to your logstash patterns_dir: "
		print "> ==== snip === <"
		print pg_patterns
		print "> ==== snip === <"
		print ""
		print "This is the filter for your log_line_prefix:\n\n%s"%(prefix_to_grok(args.prefix))


