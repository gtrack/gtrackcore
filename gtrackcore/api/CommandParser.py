from pyparsing import Forward, Word, alphas, alphanums, Literal, delimitedList, \
    Group, quotedString, pyparsing_common, Optional, ZeroOrMore


class CommandParser():
    def __init__(self, operations, btrack):
        self._operations = operations
        self._btrack = btrack

    def parseFunctionCall(self, expr):
        lPar = Literal("(").suppress()
        rPar = Literal(")").suppress()

        identifier = Word(alphas, alphanums + "_").setName('identifier')
        literal = quotedString ^ pyparsing_common.number

        functionCall = Forward()
        trackName = Group(identifier + ZeroOrMore(Literal(':') + identifier))
        trackName = trackName.setParseAction(self.trackNameAction)

        expression = (trackName ^ literal ^ functionCall).setName('expression')
        #assignment = trackName + Literal('=') + expression
        kwarg = Group(identifier + Literal('=') + expression)
        kwarg.setParseAction(self.kwArgAction)

        func_arg = kwarg | expression
        functionCall << Group(identifier + lPar + Optional(delimitedList(func_arg)) + rPar)
        functionCall = functionCall.setParseAction(self.functionCallAction)

        #statement = assignment ^ function_call
        expr = functionCall.parseString(expr)

        funcCallObj = self._evalExpression(expr[0])

        return funcCallObj

    def _evalExpression(self, expr):
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
                    trackContents = self._btrack.getTrackContentsByTrackNameAsString(arg.name)
                    a.append(trackContents)
                elif isinstance(arg, KwArg):  # kw arg
                    kw[arg.name] = arg.value
                else:  # func or literal
                    a.append(self._evalExpression(arg))
            return self._operations[expr.name](*a, **kw)
        else:  # number
            return expr

    def kwArgAction(self, tokens):
        kwArg = KwArg(tokens[0][0], tokens[0][2])

        return kwArg

    def functionCallAction(self, tokens):
        functionCall = FunctionCall(tokens[0][0], tokens[0][1:])

        return functionCall

    def trackNameAction(self, tokens):
        trackName = TrackName(''.join(tokens[0]))

        return trackName


class KwArg():
    def __init__(self, name, value):
        self.name = name
        self.value = value


class FunctionCall():
    def __init__(self, name, args):
        self.name = name
        self.args = args


class TrackName():
    def __init__(self, name):
        self.name = name

