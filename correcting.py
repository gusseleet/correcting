#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib
from subprocess import call
import os
from subprocess import Popen, PIPE


class Correcting:


    possibleFiles = []
    akronym = ''
    url = ''
    course = ''
    moment = ''
    htmlphpFolder = ''
    momentInt = 0
    pathToRoot = ''
    allLinks = []
    redovisningsText = ''
    sentences = 0
    isOk = True
    reasonOfFail = []
    pagesThatDidNotValidate = []
    pathToPhpcp = ''
    possibleNamesOnHeader = []

    def __init__(
            self,
            akronym,
            course,
            moment,
            htmlFolder,
            pathToPhpcp
    ):

        self.akronym = akronym
        self.course = course
        self.moment = moment
        self.htmlphpFolder = htmlFolder
        self.momentInt = int(float(moment[-2:]))
        self.pathToRoot = 'http://www.student.bth.se/~' + self.akronym \
                          + '/dbwebb-kurser/' + self.course + '/me/' + self.moment \
                          + '/me' + str(self.momentInt)
        self.pathToPhpcp = pathToPhpcp
        self.possibleNamesOnHeader = ['Kursmoment 0' + str(self.momentInt), 'Kmom0'
                                        + str(self.momentInt), 'kmom0'
                                        + str(self.momentInt), 'Redovisning Kmom0'
                                        + str(self.momentInt)]


    def doesUserExists(self):
        url = 'http://www.student.bth.se/~' + self.akronym
        r = urllib.urlopen(url).read()

        soup = BeautifulSoup(r)

        for link in soup.findAll('title'):
            if '404 Not Found' in link:
                return False

        return True


    def addToListIfUnieq(self, str):
        if str not in self.allLinks:
            self.allLinks.append(str)

    def addToList(self, str, list):
        if str not in list:
            list.append(str)

    def findPhpFiles(self, url):
        r = urllib.urlopen(url).read()
        soup = BeautifulSoup(r)
        self.url = url

        for table in soup.findAll('table'):
            for link in table.findAll('a'):
                fullLink = link.get_text()
                if '.php' in fullLink:
                    self.possibleFiles.append(str(fullLink))

    def findAllLinks(self):
        url = self.pathToRoot + '/me.php'
        r = urllib.urlopen(url).read()
        soup = BeautifulSoup(r)
        for link in soup.findAll('a'):
            if not 'http' in link['href']:
                url = self.pathToRoot + '/' + link['href']
                r = urllib.urlopen(url).read()
                soup = BeautifulSoup(r)
                for link1 in soup.findAll('a'):
                    if not 'http' or 'css' or 'img' or '#' or '404' \
                            in link1['href']:
                        if '?' in link1['href'][0]:
                            self.addToListIfUnieq(link['href'
                                                  ].split('.php')[0] + '.php'
                                                  + link1['href'])
                        elif 'php' in link1['href']:
                            self.addToListIfUnieq(link1['href'])

    def download(self):
        os.chdir(self.htmlphpFolder)
        call(['dbwebb', '-f', 'download', ' ' + self.moment,
              self.akronym])

    def findEndandStart(self, soup):
        for name in self.possibleNamesOnHeader:
            start = soup.find(name)
            if start != -1:
                return name
        return 'None'

    def checkingUnicorn(self):
        self.findAllLinks()
        var1 = 'http://validator.w3.org/unicorn/check?ucn_uri='
        var2 = '&ucn_task=conformance#'
        for link in self.allLinks:
            url = self.pathToRoot + '/' + link
            r = urllib.urlopen(var1 + url + var2).read()
            soup = BeautifulSoup(r)
            for aLink in soup.findAll('a', {'class': 'errors'}):
                errors = aLink.get_text()
                self.isOk = False
                self.addToList('Sida(or) validerar inte',
                               self.reasonOfFail)
                self.pagesThatDidNotValidate.append(url)

    def get_redovisnings_text(self):
        self.count_sentences()
        self.sentences = self.redovisningsText.count('.')
        if self.sentences < 15:
            self.isOk = False
            self.reasonOfFail.append('Not enought text')
        return str(self.sentences)

    def count_sentences(self):
        url = self.pathToRoot + '/report.php'
        r = urllib.urlopen(url).read()
        soup = BeautifulSoup(r)
        s = soup.get_text()
        userChosenNameStart = self.findEndandStart(s)
        intNextMoment = self.momentInt + 1
        intNextMoment = '0' + str(intNextMoment)
        userChosenNameEnd = userChosenNameStart[:-2] + intNextMoment
        start = s.find(userChosenNameStart)
        end = s.find(userChosenNameEnd)

        self.redovisningsText = s[start:end]

        return self.redovisningsText

    def validate(self):
        os.chdir(self.htmlphpFolder)
        call(['dbwebb', 'inspect', self.course, self.moment,
              self.akronym])

    def user_pass(self):
        if self.isOk is True:
            return ['Yes']
        else:
            return self.reasonOfFail

    def get_pages_not_validate(self):
        return self.pagesThatDidNotValidate

    def check_dry(self):
        os.chdir(self.pathToPhpcp)
        p = Popen(['php', 'phpcpd.phar', self.htmlphpFolder + "/" +self.moment], stdin=PIPE, stdout=PIPE, stderr=PIPE)

        output, err = p.communicate(b"input data that is passed to subprecess' stdin")


        a = output[output.find('%')-4:output.find('%')]

        if (float(a) > 0):
            print a
            self.reasonOfFail.append("Not dry")

        return output.split("\n",2)[2]


