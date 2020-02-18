"""\
Purpose: Functions for parsing SIP messages and creating SipMessage objects
Initial Version: Costas Skarakis 11/11/2018
"""
import re
from sip.SipMessage import SipMessage

ENCODING = "utf8"
MANDATORY_REQUEST_HEADERS = set(("To", "From", "CSeq", "Call-ID", "Max-Forwards", "Via"))


def buildMessage(message, parameters):
    # remove whitespace from start and end TODO test this change on existing testcases
    message = re.sub("\n +","\n",message)
    tString = message.strip().format(**parameters)
    # replace new lines
    bString = bytes(tString.replace("\n", "\r\n").replace("\r\r\n", "\r\n") + 2 * "\r\n", encoding=ENCODING)
    sipMessage = parseBytes(bString)
    return sipMessage


def parseBytes(bString, sep="\r\n", encoding=ENCODING):
    # header and body are separated by an empty line
    header, body = bString.decode(encoding).split(sep + sep, maxsplit=1)
    header_lines = header.split(sep)
    request_or_response = header_lines[0]
    headers = {}

    for line in header_lines[1:]:
        k, v = line.split(":", maxsplit=1)
        headers[str(k).strip()] = v.strip()

    # print (headers.keys())
    message = SipMessage(headers, body)
    # add more elements depending if it is a request or a responses
    resP = re.match(r"^SIP/\d\.?\d? (\d+ .*)$", request_or_response, re.I)
    if resP:
        message.type = "Response"
        message.status = resP.group(1)
        message.status_line = request_or_response
    else:
        reqP = re.match(r"^(\w+) \S+ SIP/\d\.?\d?$", request_or_response, re.I)
        if not reqP:
            raise Exception("Not a valid request or response.. or parse logic error", request_or_response)
            # return None

        # make sure all mandatory headers are present
        missing_headers = MANDATORY_REQUEST_HEADERS.difference(set(headers.keys()))
        if missing_headers:
            raise Exception("Mandatory headers missing", missing_headers)
            # return None
        message.type = "Request"
        message.request_line = request_or_response
        message.method = reqP.group(1)
    # TODO: Implement body parsing
    return message


if __name__ == "__main__":
    m = b'SIP/2.0 403 Forbidden\r\nWarning: 399 10.2.0.22 "Originating Endpoint is not configured or registered on system. Check provisioning of 3021005533, , 10.2.31.5, 10.2.0.24."\r\nCall-ID: 5bc4d2b1lKza5n\r\nCSeq: 1 OPTIONS\r\nTo: <sip:10.2.0.24:5060>\r\nFrom: <sip:3021005533@10.2.31.5:50080>;tag=snl_5bc4d2b14Y\r\nContent-Length: 0\r\nVia: SIP/2.0/TCP 10.2.31.5:50080;branch=5bc4d2b1cswcPR1cq4nQ\r\n\r\n'
    n = b'SIP/2.0 400 Bad Request\r\nWarning: 399 10.2.0.22 "Request mandatory header is missing or incorrect. Mandatory Header CSEQ-Method mismatch."\r\nVia: SIP/2.0/TCP 10.2.31.5:5080;branch=5bc619b78AKFDlh5mRGL\r\nFrom: "3021005533" <sip:3021005533@10.2.0.22:5060>;tag=snl_5bc619b7OD;epid=SCD0n\r\nCSeq: 1 OPTIONS\r\nCall-ID: 5bc619b7TTYmPW\r\nTo: <sip:10.2.0.22:5060>;tag=snl_PT47YjDdJE\r\nContent-Length: 0\r\n\r\n'
    s = parseBytes(n)
    i = '''
   REGISTER sip:10.0.0.1:5060;transport=UDP SIP/2.0
   CSeq: 0 REGISTER
   Call-ID: 1253634160-1253634161-7867113566_SubA-1253634162
   From: 7867113566 <sip:7867113566@10.0.0.1>;epid=7867113566_SubA;tag=359368062
   To: 7867113566 <sip:7867113566@10.0.0.1>
   User-Agent: 
   Expires: 300
   Contact: <sip: 7867113566@10.0.0.2:3566;lr;transport=UDP>
   Via: SIP/2.0/UDP 10.0.0.2:3566;branch=z9hG4bK359368062.17428.1
   Via: SIP/2.0/UDP 10.0.0.2:3566;branch=z9hG4bK_STANDARD_reboot_with_Authen_Proxy_3-109_1253634158-1
   Route: <sip:7867113566@10.0.0.2:5060;lr;transport=UDP>
   Path: <sip:10.0.0.2:5060;transport=UDP;lr>
   Max-Forwards: 70
   Content-Length: 0
'''
    j = buildMessage(i, {})
    s.make_response_to(j)
    print(s.contents())
    print(j.contents())
