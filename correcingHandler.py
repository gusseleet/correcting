#!/usr/bin/python
# -*- coding: utf-8 -*-
from correcting import Correcting
import argparse
import pickle
import clipboard


class CorrectingHandler:
    args = None
    correcting_ = None
    errors = []

    def __init__(self):
        self.args = None

    def get_input(self):

        parser = argparse.ArgumentParser()

        parser.add_argument('-c', type=str, action='store',
                            dest='courseName',
                            help='the current course you wanna correct')

        parser.add_argument('-m', type=str, action='store',
                            dest='momentName',
                            help='the current moment of the course')

        parser.add_argument('-a', type=str, action='store',
                            dest='acronym',
                            help='the akorym of the student')

        parser.add_argument('-af', type=str, action='store',
                            dest='folderPath',
                            help='add/change path to your htmlphp folder'
                            )

        parser.add_argument('-ap', type=str, action='store',
                            dest='phpcdpPath',
                            help='add path/change to your phpcdp folder'
                            )

        parser.add_argument('-s', action='store_true', default=False,
                            dest='boolean_switch',
                            help='Show your paths')

        parser.add_argument('--version', action='version',
                            version='%(prog)s 1.0')

        args = parser.parse_args()

        self.got_everything(args)

    def got_everything(self, args):

        course_name = args.courseName
        moment_name = args.momentName
        acronym     = args.acronym
        folder_path = args.folderPath
        pgpcdp_path = args.phpcdpPath
        show        = args.boolean_switch

        if folder_path is None:
            try:
                folder_path = pickle.load(open('save.p', 'rb'))
            except (OSError, IOError, EOFError), e:
                self.errors.append('You need to add a path to course folder'
                                   )
        else:
            pickle.dump(folder_path, open('save.p', 'wb'))

        if pgpcdp_path is None:
            try:
                pgpcdp_path = pickle.load(open('save_1.p', 'rb'))
            except (OSError, IOError, EOFError), e:
                self.errors.append('You need to add a path to phpscp')

        else:
            pickle.dump(pgpcdp_path, open('save_1.p', 'wb'))

        if show is True:

            if folder_path is None:
                print 'You have no course folder'
            else:
                print 'Coursefolder: ' + folder_path

            if pgpcdp_path is None:
                print 'You have no php path'
            else:
                print 'phpcdpPath: ' + pgpcdp_path
        elif course_name is not None and moment_name is not None \
                and acronym is not None:

            if folder_path is None and pgpcdp_path is None:
                print 'You need to add them paths'
            else:

                c = Correcting(acronym, course_name, moment_name,
                               folder_path, pgpcdp_path)
                self.run_main(c)

    def run_main(self, correcting_):

        if correcting_.doesUserExists() is False:
            print 'There is no user with that akronym'
        else:

            print '--------------------------------------------------------'
            print '-- Starting download'
            print '--------------------------------------------------------'

            print ''



            correcting_.download()

            print '-- Done'
            print ''

            print '--------------------------------------------------------'
            print '-- Starting validating'
            print '--------------------------------------------------------'

            print ''

            correcting_.validate()

            print '-- Done'
            print ''

            print '--------------------------------------------------------'
            print '-- Checking Unicorn'
            print '--------------------------------------------------------'

            print ''
            correcting_.checkingUnicorn()
            print '-- Done'
            print ''


            print '--------------------------------------------------------'
            print '-- Checking DRY'
            print '--------------------------------------------------------'
            print ''
            dry = correcting_.check_dry()
            print '-- Done'
            print ''


            print '--------------------------------------------------------'
            print '-- Checking sentences'
            print '--------------------------------------------------------'
            print ''
            print '-- Done'
            print ''

            self.user_score(correcting_, dry)

            self.createCliboard()

    def user_score(self, correcting_, dry):
        amount = correcting_.get_redovisnings_text()

        self.print_progress('-- Did student pass?')

        if 'Yes' in correcting_.user_pass():
            print "Yes" + ' (' + amount + ' sentences)'
        else:

            for item in correcting_.user_pass():
                if item == "Not enought text":
                    print item + ' (' + amount + ' sentences)'
                else:
                    print item
            print '\n'

            if "Not dry" in correcting_.user_pass():
                print dry

            if 'Sida(or) validerar inte' in correcting_.user_pass():
                print 'Sidor som inte valliderar: '
                for item in correcting_.pagesThatDidNotValidate:
                    print item

            print ''
            print "-- I added some text to your clipboard. Use CTRL + V"
            print ''
            print ''

    def createCliboard(self):

        s = "Hej, " + "\n" + "Jag har kollat på din inlämning och det ser bra ut!" + "\n" + \
            "Bra jobbat, kör vidare med nästa kursmoement."
        s = str(s)

        clipboard.copy(s.decode('utf8'))

    def print_progress(self, string):
        print '--------------------------------------------------------'
        print string
        print '--------------------------------------------------------'
        print ''
