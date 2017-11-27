import os, filecmp, random, string, subprocess

def compile(file,lang):
    if lang == 'java':
        class_file = file[:-4]+"class"
    elif lang == 'c':
        class_file = file[:-2]
    elif lang=='cpp':
        class_file = file[:-4]

    if (os.path.isfile(class_file)):
        os.remove(class_file)
    if (os.path.isfile(file)):
        if lang == 'java':
            os.system('javac '+file)
        elif lang == 'c' or lang == 'cpp':
            retcode = subprocess.call('g++ -std=c++11 '+file+' -o '+class_file, shell=True)
        if (os.path.isfile(class_file)):
            return 200
        else:
            return 400
    else:
        return 404

def run(file,input,timeout,lang, testout):
    file = file[:-4]
    if lang == 'java':
        cmd = 'java '+file
    elif lang=='c' or lang=='cpp':
        cmd = './'+file
    r = os.system('timeout '+timeout+' '+cmd+' '+input+' > ' + testout)
    if lang == 'java':
        os.remove(file+'.class')
    elif lang == 'c' or lang == 'cpp':
        os.remove(file)
    if r==0:
        return 200
    elif r==31744:
        os.remove(testout)
        return 408
    else:
        os.remove(testout)
        return 400

def match(testout, ans):
    if os.path.isfile(testout) and os.path.isfile(ans):
        b = filecmp.cmp(testout,ans)
        #os.remove('out.txt')
        return b
    else:
        return 404


def test(content, Q_ID, cursor):
    cursor.callproc('sp_getCodeAndTest', (str(Q_ID)))
    data = cursor.fetchall()
    temp_file = data[0][0] + content + data[0][1]   # code
    testCase = data[0][2]                           # test case
    testOutput = data[0][3]                         # answer
    testNum = testCase.count('\n')                  # test number

    rand = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    # prepare code and test output
    dir_path = "./code/" + rand
    dir_testOutput = dir_path + "/ans.txt"
    dir_file = dir_path + "/main.cpp"
    subprocess.call('mkdir -p ' + dir_path, shell=True)
    f = open(dir_file, 'w')
    g = open(dir_testOutput, 'w')
    f.write(temp_file)
    g.write(testOutput)
    f.close()
    g.close()

    lang = 'cpp'
    output = dir_path + "/out.txt"
    timeout = '10'

    ret = compile(dir_file, lang)
    if ret != 200:
        return ret
    print("compile success")

    for i in range(testNum):
        testcase = testCase.split('\n')[i]
        ret = run(dir_file, testcase, timeout, lang, output)
        if(ret != 200):
            return ret
    print ("run success")

    ret = match(output, dir_testOutput)
    return ret
