#!/usr/bin/python

import lldb
import fblldbbase as fb
import re

def lldbcommands():
    return [
        PrintPreambleSelf(),
        PrintPreambleArgument(),
        PrintPreambleSelector()
    ]

class PrintPreambleSelf(fb.FBCommand):
    def name(self):
        return "pself"

    def description(self):
        return "Prints the value of 'self' if the debugger is stopped in a method preamble."

    def run(self, arguments, options):
        expressionForSelf = functionPreambleExpressionForSelf()
        command = "po {}".format(expressionForSelf)
        lldb.debugger.HandleCommand(command)

class PrintPreambleArgument(fb.FBCommand):
    def name(self):
        return "parg"

    def description(self):
        return "Prints the value of an argument at index 'index' with the type 'type' if the debugger is stopped in a method preamble."

    def options(self):
        return [
            fb.FBCommandArgument(short="-a", long="--all", arg="print_all", boolean=True, default=False, help="Print all arguments.")
        ]

    def args(self):
	return [
	    fb.FBCommandArgument(arg="index", type="integer", default="0", help="Index of object argument to print. The first argument is at index 0."),
            fb.FBCommandArgument(arg="type", type="string", default="none", help="The type of the argument to print, e.g. CGRect or SEL. If no type is given, the command uses the type from the method signature.")
        ]

    def run(self, arguments, options):
        selector = functionPreambleSelector()
        numberOfParameters = selector.count(":")
        if numberOfParameters == 0:
            print "Error: The current method does not accept any arguments."
            return

        if options.print_all:
            for index in xrange(numberOfParameters):
                argType = typeNameForParameterAtIndex(index)
                expressionForArgument = functionPreambleExpressionForObjectParameterAtIndex(index, argType)
                expressionValue = fb.evaluateExpressionValue(expressionForArgument)
                if argType == "id":
                    argDescription = expressionValue.GetObjectDescription()
                elif argType == "SEL":
                    argDescription = expressionValue.GetSummary()
                else:
                    argDescription = expressionValue.GetValue()
                print "-" * 10, "ARG #{:d} ({:s})".format(index, argType), "-" * 10
                print argDescription
                if index < numberOfParameters - 1:
                    print ""
        else:
            index = int(arguments[0])
            if index > numberOfParameters - 1:
                print "Error: Parameter index {:d} out of bounds. The current method accepts {:d} argument(s).".format(index, numberOfParameters)
                return

            t = arguments[1]
            if t == "none":
                t = typeNameForParameterAtIndex(index)
                expressionForArgument = functionPreambleExpressionForObjectParameterAtIndex(index, t)
            command = "po {}".format(expressionForArgument)
            lldb.debugger.HandleCommand(command)

class PrintPreambleSelector(fb.FBCommand):
    def name(self):
        return "psel"

    def description(self):
        return "Prints the method selector if the debugger is stopped in a method preamble."

    def run(self, arguments, options):
        expressionForSelector = functionPreambleExpressionForSelector()
        if expressionForSelector is None:
            print "psel is not implemented for the {:s} architecture.".format(currentArch())
            return
        command = "exp {}".format(expressionForSelector)
        lldb.debugger.HandleCommand(command)

def currentArch():
  targetTriple = lldb.debugger.GetSelectedTarget().GetTriple()
  arch = targetTriple.split('-')[0]
  return arch

def functionPreambleSelector():
    expressionForSelector = functionPreambleExpressionForSelector()
    return fb.evaluateExpressionValue(expressionForSelector).GetSummary().strip('"')

def functionPreambleExpressionForSelf():
  arch = currentArch()
  expressionForSelf = None
  if arch == 'i386':
    expressionForSelf = '*(id*)($esp+4)'
  elif arch == 'x86_64':
    expressionForSelf = '(id)$rdi'
  elif arch == 'arm64':
    expressionForSelf = '(id)$x0'
  elif re.match(r'^armv.*$', arch):
    expressionForSelf = '(id)$r0'
  return expressionForSelf

def functionPreambleExpressionForSelector():
  arch = currentArch()
  if arch == 'i386':
    return '*(SEL*)($esp+8)'
  elif arch == 'x86_64':
    return '(SEL)$rsi'
  elif arch == 'arm64':
    return '(SEL)$x1'
  elif re.match(r'^armv.*$', arch):
    return '(SEL)$r1'
  return None

def functionPreambleExpressionForObjectParameterAtIndex(parameterIndex, t):
    arch = currentArch()
    expresssion = None
    if arch == 'i386':
        expresssion = '*({:s}*)($esp + {:d})'.format(t, 12 + parameterIndex * 4)
    elif arch == 'x86_64':
        if (parameterIndex > 3):
            raise Exception("Current implementation can not return object at index greater than 3 for arch x86_64")
        registersList = ['rdx', 'rcx', 'r8', 'r9']
        expresssion = '({:s})${:s}'.format(t, registersList[parameterIndex])
    elif arch == 'arm64':
        if parameterIndex > 5:
            raise Exception("Current implementation can not return object at index greater than 5 for arm64")  
        expresssion = '({:s})$x{:d}'.format(t, parameterIndex + 2)
    elif re.match(r'^armv.*$', arch):
        if (parameterIndex > 3):
            raise Exception("Current implementation can not return object at index greater than 1 for arm32")
        expresssion = '({:s})$r{:d}'.format(t, str(parameterIndex + 2))
    return expresssion

def encodedTypeForParameterAtIndex(parameterIndex):
    expressionForSelf = functionPreambleExpressionForSelf()
    selector = functionPreambleSelector()
    methodCallExpression = "(const char *)[[{:s} methodSignatureForSelector:(SEL)NSSelectorFromString(@\"{:s}\")] getArgumentTypeAtIndex:{:d}]".format(expressionForSelf, selector, parameterIndex + 2)
    return fb.evaluateExpressionValue(methodCallExpression).GetSummary().strip('"')

def typeNameForParameterAtIndex(parameterIndex):
    def typeNameForEncodedTypeName(encodedType):
        if encodedType == "@":
            return "id"
        elif encodedType == "c":
            return "char"
        elif encodedType == "i":
            return "int"
        elif encodedType == "s":
            return "short"
        elif encodedType == "l":
            return "long"
        elif encodedType == "q":
            return "long long"
        elif encodedType == "C":
            return "unsigned char"
        elif encodedType == "I":
            return "unsigned int"
        elif encodedType == "S":
            return "unsigned short"
        elif encodedType == "L":
            return "unsigned long"
        elif encodedType == "Q":
            return "unsigned long long"
        elif encodedType == "f":
            return "float"
        elif encodedType == "d":
            return "double"
        elif encodedType == "*":
            return "char *"
        elif encodedType == "#":
            return "Class"
        elif encodedType == ":":
            return "SEL"
        elif encodedType.startswith("{"):
            endIndex = encodedType.find("=")
            if endIndex == -1:
                return encodedType.strip("{}")
            return encodedType[1:endIndex]
        elif encodedType.startswith("^"):
            # TODO: Support for pointer-to-pointer expressions, e.g. ^^{CGRect}.
            encodedTypeName = encodedType[1:]
	    typeName = typeNameForEncodedTypeName(encodedTypeName)
            return "{:s} *".format(typeName)
        else:
            return None
    encodedType = encodedTypeForParameterAtIndex(parameterIndex)
    return typeNameForEncodedTypeName(encodedType)

