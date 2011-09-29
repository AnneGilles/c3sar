#!/usr/bin/env python
# -*- coding: utf-8 -*-

# fdf-bv-ba.py .... ummm
# fdf == data to use when filling pdf form
# bv == berechtigungsvertrag == contract to enable c3s to act as collecting society for you
# ba == bank account
#
# what we do here is generate pdfs from users data.
# user shall print, sign, fill in bank account info
# and send it back to us. (fax or snail mail)



# http://stackoverflow.com/questions/1890570/
#        how-can-i-auto-populate-a-pdf-form-in-django-python
from fdfgen import forge_fdf
import os


class C3sContract_De_Pdf():
    """
    produce and return a PDF for printout

    returns file object
    """
    def __init__(self):
        print "this is C3sContract_De_Pdf.__init__()

    return c3s_contract_de_pdf


def make_berechtigungsvertrag():
    
    pass



def gen_martins_fields():
    """
    returns a list of fields, example data

    ToDo: get data from db or request
    """
    print "getting form data..."

    fields = [
        ('surname', 'Martin'),
        ('lastname', 'Scholl'),
        ('street', 'Gerhard-Jahn-Platz'),
        ('number', '1'),
        ('postcode', '35037'),
        ('city', 'Marburg')
        ]
    return fields

def gen_martins_fdf():
    """
    generates fdf file to patch the pdf form with

    """
    #generate fdf string
    fdf = forge_fdf("", gen_martins_fields(), [], [], [])
    # write to file
    fdf_file = open("testdata_martin.fdf", "w")
    fdf_file.write(fdf)
    fdf_file.close()

    print "fdf file written."


def gen_bv_pdf_martin():
    #prepare
    gen_martins_fdf()
    print "putting data into form"
    #print os.popen('pdftk TestPdfForm.pdf fill_form testdata.fdf output formoutput.pdf flatten').read()
    print os.popen('pdftk berechtigungsvertrag-2.2.pdf fill_form testdata_martin.fdf output formoutput.pdf flatten').read()
    # berechtigungsvertrag-2.2.pdf
    print "put data into form and finalized it"
    #print os.popen('pdftk TestPdfForm.pdf fill_form testdata.fdf output output.pdf').read()
    #print "put data into form without finalizing: leaving editable"

def gen_bv_ba_martin():
    #prepare
    gen_bv_pdf_martin()
    print "combining with bank account form"
    print os.popen('pdftk formoutput.pdf bankaccount.pdf output output.pdf').read()
    print "combined personal form and bank form"
    print "pdf written to output.pdf."


if __name__ == "__main__":
    gen_bv_ba_martin()
