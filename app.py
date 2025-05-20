# app.py
from flask import Flask, render_template, request, send_file
from graphviz import Digraph
import io

app = Flask(__name__, template_folder='templates', static_folder='static')

class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        # transitions is nested: { state: { symbol: next_state, … }, … }
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = set(accept_states)

    def simulate(self, input_str):
        """Return True if input_str is accepted by this DFA."""
        current = self.start_state
        for ch in input_str:
            if current not in self.transitions or ch not in self.transitions[current]:
                return False
            current = self.transitions[current][ch]
        return current in self.accept_states

    def to_graphviz(self):
        """Build and return a Graphviz Digraph representing the DFA."""
        dot = Digraph(format='png')
        dot.attr(rankdir='LR')

        # invisible start arrow
        dot.node('', shape='none')
        dot.edge('', self.start_state)

        # draw each state
        for s in self.states:
            shape = 'doublecircle' if s in self.accept_states else 'circle'
            dot.node(s, shape=shape)

        # draw each transition
        for src, inner in self.transitions.items():
            for sym, dst in inner.items():
                dot.edge(src, dst, label=sym)

        return dot

# ----------------------------
# DFA LOGIC 
# ----------------------------
STATES = [
    'q0','q1','q2','q3','q4','q5','q6','q7','q8','q9',
    'q10','q11','q12','q13','q14','q15','q16','q17','q18','q19',
    'q20','q21','T'
]
ALPHABET = ['0','1']
TRANS = {
    'q0':  {'0':'q2',  '1':'q1'},
    'q1':  {'0':'q3',  '1':'q3'},
    'q2':  {'0':'q4',  '1':'T'},
    'q3':  {'0':'T',   '1':'q5'},
    'q4':  {'0':'q5',  '1':'q5'},
    'q5':  {'0':'q7',  '1':'q6'},
    'q6':  {'0':'q7',  '1':'q8'},
    'q7':  {'0':'q8',  '1':'q6'},
    'q8':  {'0':'q10', '1':'q9'},
    'q9':  {'0':'q11', '1':'q12'},
    'q10': {'0':'q13', '1':'q8'},
    'q11': {'0':'T',   '1':'q14'},
    'q12': {'0':'q9',  '1':'q14'},
    'q13': {'0':'q14', '1':'T'},
    'q14': {'0':'q16', '1':'q15'},
    'q15': {'0':'q16', '1':'q17'},
    'q16': {'0':'q17', '1':'q15'},
    'q17': {'0':'q19', '1':'q18'},
    'q18': {'0':'q15', '1':'q20'},
    'q19': {'0':'q20', '1':'q17'},
    'q20': {'0':'q21', '1':'q20'},
    'q21': {'0':'q21', '1':'q21'},
    'T':   {'0':'T',   '1':'T'},
}
START    = 'q0'
ACCEPT   = ['q21']

dfa = DFA(STATES, ALPHABET, TRANS, START, ACCEPT)

# ----------------------------
# Flask routes
# ----------------------------
@app.route('/', methods=['GET','POST'])
def index():
    language   = None
    result     = None
    test_str   = ''

    if request.method == 'POST':
        language = request.form.get('language')
        test_str = request.form.get('test_string', '')
        if language == 'binary':
            result = dfa.simulate(test_str)

    return render_template(
        'index.html',
        language=language,
        result=result,
        test_string=test_str )

@app.route('/dfa.png')
def dfa_png():
    """Generate the DFA diagram as PNG."""
    dot = dfa.to_graphviz()
    png_bytes = dot.pipe()
    return send_file(
        io.BytesIO(png_bytes),
        mimetype='image/png',
        as_attachment=False,
        download_name='dfa.png'
    )

if __name__ == '__main__':
    app.run(debug=True)
