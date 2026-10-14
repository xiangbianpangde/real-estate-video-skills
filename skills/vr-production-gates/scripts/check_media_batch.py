#!/usr/bin/env python3
"""Offline Matrix batch receipt check. Never calls services or retries automatically."""
import argparse
import json
from pathlib import Path


def inspect(request, response):
    requests=request['requests'];success=response['success_items'];failed=response['failed_items']
    if not isinstance(requests,list) or not requests:raise ValueError('missing_requests')
    names=[r['output_file'] for r in requests]
    if any(not isinstance(n,str) or Path(n).name!=n or not n for n in names):raise ValueError('require_unique_base_output_file')
    if len(set(names))!=len(names):raise ValueError('duplicate_request_filename')
    if type(response['code']) is not int or response['code']!=0:raise ValueError('top_level_failure')
    if not isinstance(success,list) or not isinstance(failed,list):raise ValueError('invalid_item_lists')
    counts=(len(requests),len(success),len(failed))
    actual=tuple(response[k] for k in ('total_requested','total_success','total_failed'))
    if any(type(x) is not int for x in actual) or counts!=actual:raise ValueError('count_mismatch')
    succeeded=[];nodes=[]
    for item in success:
        name=item['file_name'];node=item['node_id']
        if name not in names or not isinstance(node,str) or not node.strip():raise ValueError('unknown_success_asset')
        succeeded.append(names.index(name));nodes.append(node)
    indices=[item['index'] for item in failed]
    if any(type(i) is not int or not 0<=i<len(requests) for i in indices):raise ValueError('invalid_failed_index')
    if (len(set(nodes))!=len(nodes) or len(set(succeeded+indices))!=len(requests)
            or sorted(succeeded+indices)!=list(range(len(requests)))):raise ValueError('ambiguous_item_partition')
    if any(type(item.get('err_code')) is not int or item['err_code']!=429 for item in failed):raise ValueError('non_retryable_failure')
    return {'complete':not failed,'successful_indices':succeeded,'retry_indices':indices,
            'retry_request':{'requests':[requests[i] for i in indices]},
            'note':'Offline receipt only; delay/backoff and invocation remain caller responsibilities.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',type=Path,required=True)
    parser.add_argument('--response',type=Path,required=True)
    parser.add_argument('--retry-output',type=Path)
    args=parser.parse_args()
    try:
        result=inspect(json.loads(args.request.read_text()),json.loads(args.response.read_text()))
        if result['retry_indices'] and args.retry_output:
            # Exclusive creation preserves existing retry files and refuses planted symlinks.
            with args.retry_output.open('x',encoding='utf-8') as f:
                f.write(json.dumps(result['retry_request'],ensure_ascii=False,indent=2)+'\n')
        result.pop('retry_request')
        print(json.dumps({'passed':True,**result},ensure_ascii=False));return 0
    except (KeyError,TypeError,ValueError,OSError) as error:
        print(json.dumps({'passed':False,'complete':False,'error':str(error),'retry_indices':[]},ensure_ascii=False));return 1


if __name__=='__main__':raise SystemExit(main())
