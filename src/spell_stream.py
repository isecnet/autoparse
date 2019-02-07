"""
BSD 3-Clause License

Copyright (c) 2018, inoue.tomoya
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
import json
import pickle
import re


# noinspection SpellCheckingInspection
class LCSObject(object):

    def __init__(self, objid, seq, lineid, refmt):
        self._refmt = refmt
        if isinstance(seq, str):
            self._lcsseq = re.split(refmt, seq.strip())
        else:
            self._lcsseq = seq

        self._lineids = [lineid]
        self._pos = []
        self._sep = ' '
        self._objid = objid

    def getlcs(self, seq):
        if isinstance(seq, str):
            seq = re.split(self._refmt, seq.strip())

        count = 0
        lastmatch = -1
        for i in range(len(self._lcsseq)):
            if self._ispos(i):
                continue

            for j in range(lastmatch + 1, len(seq)):
                if self._lcsseq[i] == seq[j]:
                    lastmatch = j
                    count += 1
                    break

        return count

    def insert(self, seq, lineid):
        if isinstance(seq, str):
            seq = re.split(self._refmt, seq.strip())

        self._lineids.append(lineid)
        temp = ''
        lastmatch = -1
        placeholder = False
        for i in range(len(self._lcsseq)):
            if self._ispos(i):
                if not placeholder:
                    temp += '* '

                placeholder = True
                continue

            for j in range(lastmatch + 1, len(seq)):
                if self._lcsseq[i] == seq[j]:
                    placeholder = False
                    temp += self._lcsseq[i] + ' '
                    lastmatch = j
                    break
                elif not placeholder:
                    temp += '* '
                    placeholder = True

        temp = temp.strip()
        self._lcsseq = re.split(self._refmt, temp)
        self._pos = self._getpos()
        self._sep = self._getsep()

    def tojson(self):
        temp = ''
        for i in self._lcsseq:
            temp += i + ' '

        return json.dumps({
            'lcsseq': temp,
            'lineids': self._lineids,
            'position': self._pos
        })

    def __len__(self):
        return len(self._lcsseq)

    def param(self, seq):
        if isinstance(seq, str):
            seq = re.split(self._refmt, seq.strip())

        j = 0
        ret = []
        for i in range(len(self._lcsseq)):
            slot = []
            if self._ispos(i):
                while j < len(seq):
                    if i != (len(self._lcsseq) - 1) and self._lcsseq[i + 1] == seq[j]:
                        break
                    else:
                        slot.append(seq[j])

                    j += 1

                ret.append(slot)
            elif self._lcsseq[i] != seq[j]:
                return None
            else:
                j += 1

        if j != len(seq):
            return None

        return ret

    def reparam(self, seq):
        if isinstance(seq, list):
            seq = ' '.join(seq)

        seq = seq.strip()
        ret = []
        print(self._sep)
        print(seq)
        p = re.split(self._sep, seq)
        for i in p:
            if len(i) != 0:
                ret.append(re.split(self._refmt, i.strip()))

        if len(ret) == len(self._pos):
            return ret

        return None

    def _ispos(self, idx):
        for i in self._pos:
            if i == idx:
                return True

        return False

    @staticmethod
    def _tcat(seq, s, e):
        sub = ''
        for i in range(s, e + 1):
            sub += seq[i] + ' '

        return sub.rstrip()

    def _getsep(self):
        sep_token = []
        s, e = 0, 0
        for i in range(len(self._lcsseq)):
            if self._ispos(i):
                if s != e:
                    sep_token.append(self._tcat(self._lcsseq, s, e))

                s = i + 1
                e = s
            else:
                e = i

            if e == len(self._lcsseq) - 1:
                sep_token.append(self._tcat(self._lcsseq, s, e))
                break

        ret = ''
        for i in range(len(sep_token)):
            if i == len(sep_token) - 1:
                ret += sep_token[i]
            else:
                ret += sep_token[i] + '|'

        return ret

    def _getpos(self):
        pos = []
        for i in range(len(self._lcsseq)):
            if self._lcsseq[i] == '*':
                pos.append(i)

        return pos

    def getobjid(self):
        return self._objid


# noinspection SpellCheckingInspection
class LCSMap(object):

    def __init__(self, refmt):
        self._refmt = refmt
        self._lcsobjs = []
        self._lineid = 0
        self._objid = 0

    def insert(self, entry):
        seq = re.split(self._refmt, entry.strip())
        obj = self.match(seq)
        if obj is None:
            self._lineid += 1
            obj = LCSObject(self._objid, seq, self._lineid, self._refmt)
            self._lcsobjs.append(obj)
            self._objid += 1
        else:
            self._lineid += 1
            obj.insert(seq, self._lineid)

        return obj

    def match(self, seq):
        if isinstance(seq, str):
            seq = re.split(self._refmt, seq.strip())

        bestmatch = None
        bestmatch_len = 0
        seqlen = len(seq)
        for obj in self._lcsobjs:
            objlen = len(obj)
            if objlen < (seqlen / 2) or objlen > (seqlen * 2):
                continue

            lcs = obj.getlcs(seq)
            if lcs >= (seqlen / 2) and lcs > bestmatch_len:
                bestmatch = obj
                bestmatch_len = lcs

        return bestmatch

    def __getitem__(self, idx):
        return self._lcsobjs[idx]

    def __len__(self):
        return len(self._lcsobjs)

    def __dir__(self):
        for i in self._lcsobjs:
            print(i.tojson())


# noinspection SpellCheckingInspection
def save(filename, lcsmap):
    if type(lcsmap) == LCSMap:
        with open(filename, 'wb') as f:
            pickle.dump(lcsmap, f)
    else:
        if __debug__ is True:
            print('%s isn\'t slm object' % filename)


def load(filename):
    with open(filename, 'rb') as f:
        slm = pickle.load(f)
        if type(slm) == LCSMap:
            return slm

        if __debug__ is True:
            print('%s isn\'t slm object' % filename)

        return None