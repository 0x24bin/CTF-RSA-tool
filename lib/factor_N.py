# coding:utf-8
import requests
from bs4 import BeautifulSoup
import subprocess
import libnum
import wiener_attack


def solve(N, e, sageworks):
    if sageworks:
        return factordb(N) or p_q_2_close(N) or wiener_attack.solve(N, e) or smallq(N) or boneh_durfee(N, e) or None
    else:
        return factordb(N) or p_q_2_close(N) or wiener_attack.solve(N, e) or smallq(N) or None


def factordb(N):
    res = requests.get('http://factordb.com/index.php?query=' + str(N))
    soup = BeautifulSoup(res.text, 'lxml')
    factor = []
    for i in soup.find_all('font'):
        if i.string and '.' not in str(i.string) and '*' not in str(i.string):
            factor.append(int(i.string))
    while N in factor:
        factor.remove(N)
    if len(factor) is 2:
        return factor
    else:
        return


def boneh_durfee(N, e):
    # use boneh durfee method, should return a d value, else returns 0
    # only works if the sageworks() function returned True
    # many of these problems will be solved by the wiener attack module but perhaps some will fall through to here
    # TODO: get an example public key solvable by boneh_durfee but not wiener
    sageresult = int(subprocess.check_output(
        ['sage', 'lib/boneh_durfee.sage', str(N), str(e)]))
    if sageresult > 0:
        # use PyCrypto _slowmath rsa_construct to resolve p and q from d
        from Crypto.PublicKey import _slowmath
        tmp_priv = _slowmath.rsa_construct(
            long(N), long(e), d=long(sageresult))
        p = tmp_priv.p
        q = tmp_priv.q
        # d = sageresult
        return p, q


def smallq(N):
    # Try an attack where q < 100,000, from BKPCTF2016 - sourcekris
    for prime in libnum.primes(100000):
        if N % prime == 0:
            q = prime
            p = N / q
    return p, q


def isqrt(n):
    x = n
    y = (x + n // x) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


# |p-q|较小
def p_q_2_close(n):
    a = isqrt(n)
    b2 = a * a - n
    b = isqrt(n)
    count = 0
    while b * b != b2:
        a = a + 1
        b2 = a * a - n
        b = isqrt(b2)
        count += 1
    p = a + b
    q = a - b
    assert n == p * q
    return p, q


if __name__ == '__main__':
    print 'test factordb'
    print solve(23)
    print solve(87924348264132406875276140514499937145050893665602592992418171647042491658461)
    print 'test |p-q|较小'
    n = 966808932627497190635859236054960349099463975227350564265384373280336699853387254070662881265937565163000758606154308757944030571837175048514574473061401566330836334647176655282619268592560172726526643074499534129878217409046045533656897050117438496357231575999185527675071002803951800635220029015932007465117818739948903750200830856115668691007706836952244842719419452946259275251773298338162389930518838272704908887016474007051397194588396039111216708866214614779627566959335170676055025850932631053641576566165694121420546081043285806783239296799795655191121966377590175780618944910532816988143056757054052679968538901460893571204904394975714081055455240523895653305315517745729334114549756695334171142876080477105070409544777981602152762154610738540163796164295222810243309051503090866674634440359226192530724635477051576515179864461174911975667162597286769079380660782647952944808596310476973939156187472076952935728249061137481887589103973591082872988641958270285169650803792395556363304056290077801453980822097583574309682935697260204862756923865556397686696854239564541407185709940107806536773160263764483443859425726953142964148216209968437587044617613518058779287167853349364533716458676066734216877566181514607693882375533
    print p_q_2_close(n)
