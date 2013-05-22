#!/usr/bin/env python

from php import PHP

def main():
	php = PHP()
	php.include('tcpdf/config/lang/eng.php')
	php.include('tcpdf/tcpdf.php')

	pdf = php.new('TCPDF', 'P', 'mm', 'A4', True, 'UTF-8')
	
	pdf.setFontSubsetting(False)
	pdf.setAuthor('VSzA')
	pdf.setCreator('PPCG')
	pdf.setTitle('TCPDF in Python!?')
	pdf.setPrintHeader(False)
	pdf.setMargins(10, 10)

	pdf.AddPage()
	pdf.SetFont('dejavusans', 'B', 12)
	pdf.Cell(0, 0, 'Hello Python')
	pdf.Ln()

	x = pdf.GetX()
	y = pdf.GetY()
	pdf.setXY(30, 30)
	pdf.Cell(0, 0, 'GOTOs are bad')
	pdf.setXY(x, y + 2.5)
	pdf.Cell(0, 0, 'I can has PHP variables')

	pdf.Output()
	pdf_data = str(php)

	with file('output.pdf', 'wb') as pdf_file:
		pdf_file.write(pdf_data)
	print '{0} bytes of PDF have been written'.format(len(pdf_data))


if __name__ == '__main__':
	main()
