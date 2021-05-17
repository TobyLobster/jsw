import re

def add_values_in_dict(sample_dict, key, list_of_values):
    """Append multiple values to a key in the given dictionary"""
    if key not in sample_dict:
        sample_dict[key] = list()
    sample_dict[key].extend(list_of_values)
    return sample_dict

def processFile(lines, outputFilename, prefix):
    outlines = []
    variables = []
    labels = []

    for line in lines:
        hasMnemonic = re.search("\W(ADC|AND|ASL|BCC|BCS|BEQ|BIT|BMI|BNE|BPL|BRK|BVC|BVS|CLC|CLD|CLI|CLV|CMP|CPX|CPY|DEC|DEX|DEY|EOR|INC|INX|INY|JMP|JSR|LDA|LDX|LDY|LSR|NOP|ORA|PHA|PHP|PLA|PLP|ROL|ROR|RTI|RTS|SBC|SEC|SED|SEI|STA|STX|STY|TAX|TAY|TSX|TXA|TXS|TYA)(\W|$)", line)
        if (hasMnemonic):
            line = re.sub("^\&[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F] ([0-9a-fA-F][0-9a-fA-F] )+", "", line)
            match = re.match("\s*((ADC|AND|ASL|BCC|BCS|BEQ|BIT|BMI|BNE|BPL|BRK|BVC|BVS|CLC|CLD|CLI|CLV|CMP|CPX|CPY|DEC|DEX|DEY|EOR|INC|INX|INY|JMP|JSR|LDA|LDX|LDY|LSR|NOP|ORA|PHA|PHP|PLA|PLP|ROL|ROR|RTI|RTS|SBC|SEC|SED|SEI|STA|STX|STY|TAX|TAY|TSX|TXA|TXS|TYA)(.*))", line)
            if (match):
                line = "    " + match.group(1)[0:3].lower() + match.group(1)[3:]
                line = line.replace("asl A", "asl", 1)
                line = line.replace("lsr A", "lsr", 1)
                line = line.replace("rol A", "rol", 1)
                line = line.replace("ror A", "ror", 1)
                if (line.find(';') < 0):
                    line = line + "; "
        else:
            match = re.match("^\&[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F] (([0-9a-fA-F][0-9a-fA-F] )+)", line + " ")
            if (match):
                remainder = line[match.span()[1]:].strip()
                if (len(remainder) > 0):
                    if (remainder[0] != ';'):
                        remainder = ";" + remainder
                line = "    !byte $" + match.group(1).strip().replace(" ", ", $") + " " + remainder
        match = re.match(" ?; +([a-zA-Z_'][a-zA-Z_'0-9]+)( *)(.*)", line)
        if (match):
            line = match.group(1).replace("'", "");
            if match.group(3):
                removedHash = match.group(3)
                if (removedHash[0] == '#'):
                    removedHash = removedHash[1:]
                line = line + match.group(2) + " ; " + removedHash
        line = line.replace("  #", "  ;", 1)
        line = line.replace("&", "$")
        line = re.sub("^#", ";", line)
        line = re.sub("\#\$00(\W)", r"#0  \1", line)
        line = re.sub("\#\$01(\W)", r"#1  \1", line)
        line = re.sub("\#\$02(\W)", r"#2  \1", line)
        line = re.sub("\#\$03(\W)", r"#3  \1", line)
        line = re.sub("\#\$04(\W)", r"#4  \1", line)
        line = re.sub("\#\$05(\W)", r"#5  \1", line)
        line = re.sub("\#\$06(\W)", r"#6  \1", line)
        line = re.sub("\#\$07(\W)", r"#7  \1", line)
        line = re.sub("\#\$08(\W)", r"#8  \1", line)
        line = re.sub("\#\$09(\W)", r"#9  \1", line)

        line = re.sub("^[Uu]nused", "; Unused", line)
        line = re.sub("\([Uu]nused\)", "; Unused", line)
        line = re.sub("[Uu]nused", "[unused]", line)
        line = line.replace("didn't_", "didnt_")
        line = line.replace("isn't_", "isnt_")
        line = line.replace("can't_", "cant_")

        if (len(line) > 0):
            match = re.match("^([a-zA-Z_][a-zA-Z_0-9]*)", line)
            if (match):
                labels.append(match.group(1))

        if (line.find('#') < 0):
            if (line.find('$') >= 0):
                if (line.find(';') >= 0):
                    match = re.search("; ([a-zA-Z0-9_]+)$", line);
                    if (match):
                        hasMnemonic = re.search("\W(adc|and|asl|bcc|bcs|beq|bit|bmi|bne|bpl|brk|bvc|bvs|clc|cld|cli|clv|cmp|cpx|cpy|dec|dex|dey|eor|inc|inx|iny|jmp|jsr|lda|ldx|ldy|lsr|nop|ora|pha|php|pla|plp|rol|ror|rti|rts|sbc|sec|sed|sei|sta|stx|sty|tax|tay|tsx|txa|txs|tya)(\W|$)", line)
                        if (hasMnemonic):
                            fullAddr = re.search("\$([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])(\W|$)", line)
                            if (fullAddr):
                                addr = fullAddr.group(1)
                                variables.append((addr, match.group(1)))
                            zpAddr = re.search("\$([0-9A-Fa-f][0-9A-Fa-f])(\W|$)", line)
                            if (zpAddr):
                                addr = zpAddr.group(1)
                                variables.append((addr, match.group(1)))

        outlines.append(line)


    labels = sorted(set(labels))
    variables = sorted(set(variables), key=lambda var: var[0].zfill(4))
    dictVar = dict()
    for variable in variables:
        add_values_in_dict(dictVar, variable[0], [variable[1]])

    i = 0
    newlines = []
    for line in outlines:
        newline = line
        if (line.find('#') < 0):
            if (line.find('$') >= 0):
                hasMnemonic = re.search("\W(adc|and|asl|bcc|bcs|beq|bit|bmi|bne|bpl|brk|bvc|bvs|clc|cld|cli|clv|cmp|cpx|cpy|dec|dex|dey|eor|inc|inx|iny|jmp|jsr|lda|ldx|ldy|lsr|nop|ora|pha|php|pla|plp|rol|ror|rti|rts|sbc|sec|sed|sei|sta|stx|sty|tax|tay|tsx|txa|txs|tya)(\W|$)", line)
                if (hasMnemonic):
                    fullAddr = re.search("\$([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])(\W|$)", line)
                    if (fullAddr):
                        addr = fullAddr.group(1)
                        if (addr in dictVar):
                            listOfPossibleVariables = dictVar[addr]
                            varToUse = listOfPossibleVariables[0]
                            for possVar in listOfPossibleVariables:
                                if (newline.endswith("; " + possVar)):
                                    varToUse = possVar
                                if (newline.find("; " + possVar + " ;") >= 0):
                                    varToUse = possVar

                            newline = line[0:fullAddr.span(1)[0] - 1] + varToUse + line[fullAddr.span(1)[1]:]

                            if (newline.endswith("; " + varToUse)):
                                newline = newline[:len(newline) - len(varToUse)]

                            found = newline.find("; " + varToUse + " ")
                            if (found >= 0):
                                newline = newline[:found] + newline[found + len(varToUse) + 2:]

                    fullAddr = re.search("\$([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])(\W|$)", line)
                    zpAddr = re.search("\$([0-9A-Fa-f][0-9A-Fa-f])(\W|$)", line)
                    if (zpAddr):
                        addr = zpAddr.group(1)
                        if (addr in dictVar):
                            listOfPossibleVariables = dictVar[addr]
                            varToUse = listOfPossibleVariables[0]
                            for possVar in listOfPossibleVariables:
                                if (newline.endswith("; " + possVar)):
                                    varToUse = possVar
                                if (newline.find("; " + possVar + " ;") >= 0):
                                    varToUse = possVar

                            newline = line[0:zpAddr.span(1)[0] - 1] + varToUse + line[zpAddr.span(1)[1]:]
                            if (newline.endswith("; " + varToUse)):
                                newline = newline[:len(newline) - len(varToUse)]

                            found = newline.find("; " + varToUse + " ")
                            if (found >= 0):
                                newline = newline[:found] + newline[found + len(varToUse) + 2:]

        if ((len(newline) > 0) and (newline[0] != ";")):
            lineParts = newline.split(';')
            if (len(lineParts) > 1):
                newline = lineParts[0].rstrip().ljust(51)
                newline = newline + " ; " + lineParts[1].strip()
                if (len(lineParts) > 2):
                    newline = newline + " ; " + lineParts[2].strip()
                    if (len(lineParts) > 3):
                        newline = newline + " ; " + lineParts[3].strip()
        newlines.append(newline + "\n")
        i += 1

    newlines.insert(0, "\n");
    variables.reverse()
    for variable in variables:
        if (not variable[1] in labels):
            newlines.insert(0, variable[1].ljust(51) + " = $" + variable[0] + "\n")

    newlines.insert(0, "\n; variables\n");
    newlines.insert(0, prefix + "\n")

    with open(outputFilename, 'w') as f:
        f.writelines(newlines)


    # print('\n'.join(map(str, labels)))

with open('jsw1.dis') as f:
    lines = f.read().splitlines()
    processFile(lines, 'jsw1.a', "*= $0b00")

with open('jsw2.dis') as f:
    lines = f.read().splitlines()
    processFile(lines, 'jsw2.a', "*= $4e00")
