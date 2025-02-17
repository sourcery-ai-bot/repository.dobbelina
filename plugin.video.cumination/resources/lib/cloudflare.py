
#
#      Copyright (C) 2015 tknorris (Derived from Mikey1234's & Lambda's)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
#  This code is a derivative of the YouTube plugin for XBMC and associated works
#  released under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 3


import re
from six.moves import urllib_error, urllib_parse, urllib_request

import xbmc


USER_AGENT = "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"

MAX_TRIES = 6
COMPONENT = __name__


class NoRedirection(urllib_request.HTTPErrorProcessor):
    def http_response(self, request, response):
        xbmc.log('Stopping Redirect')
        return response

    https_response = http_response


def solve_equation(equation):
    try:
        offset = 1 if equation[0] == '+' else 0
        return int(eval(equation.replace('!+[]', '1').replace('!![]', '1').replace('[]', '0').replace('(', 'str(')[offset:]))
    except:
        pass


def solve(url, cj, user_agent=None, wait=True):
    if user_agent is None:
        user_agent = USER_AGENT
    headers = {'User-Agent': user_agent, 'Referer': url}
    if cj is not None:
        try:
            cj.load(ignore_discard=True)
        except:
            pass
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cj))
        urllib_request.install_opener(opener)

    request = urllib_request.Request(url)
    for key, value in headers.items():
        request.add_header(key, value)
    try:
        response = urllib_request.urlopen(request)
        html = response.read()
    except urllib_error.HTTPError as e:
        html = e.read()

    tries = 0
    solver_pattern = r'var (?:s,t,o,p,b,r,e,a,k,i,n,g|t,r,a),f,\s*([^=]+)={"([^"]+)":([^}]+)};.+challenge-form\'\);.*?\n.*?;(.*?);a\.value'
    vc_pattern = 'input type="hidden" name="jschl_vc" value="([^"]+)'
    pass_pattern = 'input type="hidden" name="pass" value="([^"]+)'
    while tries < MAX_TRIES:
        init_match = re.search(solver_pattern, html, re.DOTALL)
        vc_match = re.search(vc_pattern, html)
        pass_match = re.search(pass_pattern, html)

        if not init_match or not vc_match or not pass_match:
            xbmc.log(
                f"Couldn't find attribute: init: |{init_match}| vc: |{vc_match}| pass: |{pass_match}| No cloudflare check?"
            )
            return False

        init_dict, init_var, init_equation, equations = init_match.groups()
        vc = vc_match[1]
        password = pass_match[1]

        # log_utils.log("VC is: %s" % (vc), xbmc.LOGDEBUG, COMPONENT)
        varname = (init_dict, init_var)
        result = int(solve_equation(init_equation.rstrip()))
        xbmc.log(f'Initial value: |{init_equation}| Result: |{result}|')

        for equation in equations.split(';'):
            equation = equation.rstrip()
            if equation[:len('.'.join(varname))] != '.'.join(varname):
                xbmc.log(f'Equation does not start with varname |{equation}|')
            else:
                equation = equation[len('.'.join(varname)):]

            expression = equation[2:]
            operator = equation[0]
            if operator not in ['+', '-', '*', '/']:
                # log_utils.log('Unknown operator: |%s|' % (equation), log_utils.LOGWARNING, COMPONENT)
                continue

            result = int(str(eval(str(result) + operator + str(solve_equation(expression)))))
                    # log_utils.log('intermediate: %s = %s' % (equation, result), log_utils.LOGDEBUG, COMPONENT)

        scheme = urllib_parse.urlparse(url).scheme
        domain = urllib_parse.urlparse(url).hostname
        result += len(domain)
        # log_utils.log('Final Result: |%s|' % (result), log_utils.LOGDEBUG, COMPONENT)

        if wait:
            # log_utils.log('Sleeping for 5 Seconds', log_utils.LOGDEBUG, COMPONENT)
            xbmc.sleep(5000)

        url = f'{scheme}://{domain}/cdn-cgi/l/chk_jschl?jschl_vc={vc}&jschl_answer={result}&pass={urllib_parse.quote(password)}'
        # log_utils.log('url: %s' % (url), log_utils.LOGDEBUG, COMPONENT)
        request = urllib_request.Request(url)
        for key, value_ in headers.items():
            request.add_header(key, value_)
        try:
            opener = urllib_request.build_opener(NoRedirection)
            urllib_request.install_opener(opener)
            response = urllib_request.urlopen(request)
            while response.getcode() in [301, 302, 303, 307]:
                if cj is not None:
                    cj.extract_cookies(response, request)

                redir_url = response.info().getheader('location')
                if not redir_url.startswith('http'):
                    base_url = f'{scheme}://{domain}'
                    redir_url = urllib_parse.urljoin(base_url, redir_url)

                request = urllib_request.Request(redir_url)
                for key, value__ in headers.items():
                    request.add_header(key, value__)
                if cj is not None:
                    cj.add_cookie_header(request)

                response = urllib_request.urlopen(request)
            final = response.read()
            if 'cf-browser-verification' not in final:
                break
            # log_utils.log('CF Failure: html: %s url: %s' % (html, url), log_utils.LOGWARNING, COMPONENT)
            tries += 1
            html = final
        except urllib_error.HTTPError as e:
            # log_utils.log('CloudFlare HTTP Error: %s on url: %s' % (e.code, url), log_utils.LOGWARNING, COMPONENT)
            return False
        except urllib_error.URLError as e:
            # log_utils.log('CloudFlare URLError Error: %s on url: %s' % (e, url), log_utils.LOGWARNING, COMPONENT)
            return False

    if cj is not None:
        cj.save()

    return final
