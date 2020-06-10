import re
import json
import os

# Assume we're running from the repository root (one folder above this file)
filepath = 'public/static/main.js'

JS_TEMPLATE = '''
metrics = %s;

function click_button(){
    console.log('click_button');
    $('button').filter('.gorilla-metrics-add').trigger('click');
    setTimeout(write_fields, 100);
}

function write_fields(){
    let metric = metrics.pop();
    console.log(metric);
    $('div[data-field="key"] > input'  ).last().val(metric).trigger('change');
    $('div[data-field="title"] > input').last().val(metric).trigger('change');
    if(metrics.length > 0) {
        setTimeout(click_button, 100);
    }
};

click_button();

'''

def get_page_metrics(filepath: str, verbose=False):
    '''
    Quick-and-dirty regular expressions to find the keys in the `state` object.

    args:
        filepath: Path to the `main.js` JavaScript file

    returns:
        List of metric names

    Example:

    ```
    let state = {
        key1: "value1",
        key2: "value2"
    }
    ```

    -> ['key1', 'key2']

    This should probably be done more reliably using a lexer like slimit.
    https://slimit.readthedocs.io/en/latest/

    '''
    with open(filepath, 'r') as f:
        contents = f.read().split('\n')

    ix0 = None
    for i, line in enumerate(contents):
        if re.search('let state = {', line):
            ix0 = i+1
            depth = 1
            continue
        if ix0 is not None:
            if re.search('{', line):
                depth += 1
            if re.search('}', line):
                depth -= 1
            if depth == 0:
                ix1 = i
                break

    state_code = contents[ix0:ix1]

    if verbose:
        print('\nFound state declaration:\n')
        print('\n'.join(state_code))

    def get_metric(line):
        m = re.findall('([a-z].+):', line)
        if len(m) > 0:
            return m[0]

    metrics = [get_metric(line) for line in state_code]
    metrics = [m for m in metrics if m is not None]

    if verbose:
        print('\nFound metrics:\n')
        print(metrics)
    return metrics

metrics = get_page_metrics(filepath, verbose=True)

output = JS_TEMPLATE % (str(metrics))

print('\n\n---\n\nNow go to the Metrics tab in the Gorilla code editor, open up a JavaScript console, and paste the following (+ press Return):\n')
print(output)
