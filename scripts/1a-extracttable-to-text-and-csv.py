from ExtractTable import ExtractTable
def run_et(file):
    et_sess = ExtractTable(api_key = '[ENTER API KEY]')
    print(et_sess.check_usage())
    table_data = et_sess.process_file(filepath = 'comparison-input-data/{}'.format(file), pages='all', output_format='df')
    et_sess.save_output('comparison-output-data/extracttable')


files = ['scan1.pdf', 'scan2.pdf', 'scan3.png']
[run_et(f) for f in files]