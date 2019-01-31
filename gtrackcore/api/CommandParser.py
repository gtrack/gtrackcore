from pyparsing import Forward, Word, alphas, alphanums, Literal, delimitedList, \
    Group, quotedString, pyparsing_common, Optional


def parse():
    lparen = Literal("(").suppress()
    rparen = Literal(")").suppress()

    identifier = Word(alphas, alphanums + "_").setName('identifier')

    literal = quotedString ^ pyparsing_common.number

    function_call = Forward()
    trackName = Group(identifier + Literal(':') + identifier)
    trackName = trackName.setParseAction(trackNameAction)

    expression = (trackName ^ literal ^ function_call).setName('expression')

    assignment = trackName + Literal('=') + expression

    kwarg = Group(identifier + Literal('=') + expression)
    kwarg.setParseAction(kwArgAction)

    func_arg =  kwarg | expression

    function_call << Group(identifier + lparen + Optional(delimitedList(func_arg)) + rparen)
    function_call = function_call.setParseAction(functionCallAction)

    statement = assignment ^ function_call

    stm = statement.parseString("output:t4=complement(intersect(union(input:t1, input:t2)), input:t3, set=123)")
    #print stm
    name, _, value = stm
    evalExpression(value)

class KwArg():
    pass

def kwArgAction(tokens):
    kwArg = KwArg()
    kwArg.name = tokens[0][0]
    kwArg.value = tokens[0][2]

    return kwArg

class FunctionCall():
    pass

def functionCallAction(tokens):
    functionCall = FunctionCall()
    functionCall.name = tokens[0][0]
    functionCall.args = tokens[0][1:]

    return functionCall

class TrackName():
    pass

def trackNameAction(tokens):
    trackName = TrackName()
    trackName.name = ''.join(tokens[0])
    return trackName


def evalExpression(expr):
    if isinstance(expr, str):
        if expr[0] in '"\'':  # string literal
            return expr[1:-1]  # remove quotes
        else:
            "unrecognized"
    elif isinstance(expr, FunctionCall):
        a = []
        kw = {}
        for arg in expr.args:
            if isinstance(arg, TrackName):
                a.append(arg.name)
            elif isinstance(arg, KwArg): #kw arg
                kw[arg.name] = arg.value
            else: #func or literal
                a.append(evalExpression(arg))
        # funcs[expr.name](*a, **kw)
        print "method call: args: " + str(a) + ' kwarg: ' + str(kw)
        return 'call method here'

    else: # number
        return expr


if __name__ == '__main__':
    parse()

