import pyparsing as pp


class CommandParser():
    def __init__(self, operations, btrack):
        self._operations = operations
        self._btrack = btrack

    def parse(self, expr):
        lPar = pp.Literal("(").suppress()
        rPar = pp.Literal(")").suppress()

        literalTrue = pp.Keyword('true', caseless=True)
        literalTrue.setParseAction(pp.replaceWith(True))
        literalFalse = pp.Keyword('false', caseless=True)
        literalFalse.setParseAction(pp.replaceWith(False))
        booleanLiteral = literalTrue ^ literalFalse
        # literal is a quoted string, a number or a boolean value
        literal = pp.quotedString ^ pp.pyparsing_common.number ^ booleanLiteral

        # identifier consists of alphanumeric chars or _
        identifier = pp.Word(pp.alphas, pp.alphanums + "_").setName('identifier')
        # track name is one or more identifiers connected by :
        trackName = pp.Group(identifier + pp.ZeroOrMore(pp.Literal(':') + identifier))
        trackName = trackName.setParseAction(self.trackNameAction)

        functionCall = pp.Forward()
        # expression is a trackname, a literal or a function call
        expression = (trackName ^ literal ^ functionCall).setName('expression')
        # assignment is a trackname followed by = and a function call
        assignment = pp.Group(trackName + pp.Literal('=') + functionCall)
        assignment = assignment.setParseAction(self.assignmentAction)
        # function keyword argument value is a literal
        kwargValue = literal
        # function keyword argument is and identifier followed by = and keyword argument value
        kwarg = pp.Group(identifier + pp.Literal('=') + kwargValue)
        kwarg.setParseAction(self.kwArgAction)

        # function argument can be either a keyword argument or an expression
        func_arg = kwarg | expression
        # function call consistes of en identifier and ([optionally arguments])
        functionCall << pp.Group(identifier + lPar + pp.Optional(pp.delimitedList(func_arg)) + rPar)
        functionCall = functionCall.setParseAction(self.functionCallAction)
        # a statement if either assignment or a function call
        statement = assignment ^ functionCall

        parsedStatement = statement.parseString(expr)
        if isinstance(parsedStatement[0], FunctionCall):
            funcCallObj = self._evalExpression(parsedStatement[0])

            return funcCallObj
        elif isinstance(parsedStatement[0], Assignment):
            funcCallObj = self._evalExpression(parsedStatement[0].value)
            if not funcCallObj:
                return
            assignment = (parsedStatement[0].name, funcCallObj)

            return assignment

    def _evalExpression(self, expr):
        # evaluating string literal
        if isinstance(expr, str):
            if expr[0] in '"\'':  # string literal
                return expr[1:-1]  # remove quotes
            else:
                "Unrecognized element - can't evaluate"
        # evaluating function call
        elif isinstance(expr, FunctionCall):
            a = []
            kw = {}
            for arg in expr.args:
                # track name
                if isinstance(arg, TrackName):
                    tcWrapper = self._btrack.getTrackContentsByTrackNameAsString(arg.name)
                    if not tcWrapper:
                        print 'Track with name ' + arg.name + ' not found'
                        return
                    trackContents = tcWrapper.getTrackContents()
                    a.append(trackContents)
                # keyword argument
                elif isinstance(arg, KwArg):
                    kw[arg.name] = arg.value
                # function call or literal
                else:
                    a.append(self._evalExpression(arg))
            return self._operations[expr.name](*a, **kw)
        # evaluating number or boolean literal
        else:
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

    def assignmentAction(self, tokens):
        if isinstance(tokens[0][0], TrackName):
            name = tokens[0][0].name
        else:
            name = tokens[0][0]
        assignment = Assignment(name, tokens[0][2])

        return assignment


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


class Assignment():
    def __init__(self, name, value):
        self.name = name
        self.value = value
