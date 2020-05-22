#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This software has been developed by:

    GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

'''
This file contains functions related to the Cufflinks process used in both console
mode and gui mode.
'''

#-------------------------------------------------------------------------------

import os
import re
import sys

import xbioinfoapp
import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def create_cufflinks_cuffmerge_config_file(experiment_id='exp001', reference_dataset_id='Athaliana', reference_file='Arabidopsis_thaliana.TAIR10.dna.toplevel.fa', annotation_file='Arabidopsis_thaliana.TAIR10.36.gtf', mask_file='NONE', alignment_dataset_id_list=['star-170101-235959','tophat-170101-235959']):
    '''
    Create Cufflinks-Cuffmerge config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # create the Cufflinks-Cuffmerge config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_cufflinks_cuffmerge_config_file())):
            os.makedirs(os.path.dirname(get_cufflinks_cuffmerge_config_file()))
        with open(get_cufflinks_cuffmerge_config_file(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# The reference and GTF files have to be located in the cluster directory {0}/experiment_id/reference_dataset_id'.format(xlib.get_cluster_reference_dir())))
            file_id.write( '{0}\n'.format('# The experiment_id, reference_dataset_id, reference_file, gtf_guide and mask_file names are fixed in the identification section.'))
            file_id.write( '{0}\n'.format('# The alignment files have to be located in the cluster directory {0}/experiment_id/alignment_dataset_id'.format(xlib.get_cluster_result_dir())))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# You can consult the parameters of Cufflinks and Cuffmerge, and their meaning in http://cole-trapnell-lab.github.io/cufflinks/.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# In section "Cufflinks parameters", the key "other_parameters" allows you to input additional parameters in the format:'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('#    other_parameters = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# parameter-i is a parameter name of Cufflinks and value-i a valid value of parameter-i, e.g.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('#    other_parameters = --label; --min-intron-length=50'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information identifies the experiment.'))
            file_id.write( '{0}\n'.format('[identification]'))
            file_id.write( '{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write( '{0:<50} {1}\n'.format('reference_dataset_id = {0}'.format(reference_dataset_id), '# reference dataset identification'))
            file_id.write( '{0:<50} {1}\n'.format('reference_file = {0}'.format(reference_file), '# reference file name'))
            file_id.write( '{0:<50} {1}\n'.format('gtf_guide = {0}'.format(annotation_file), '# reference annotation file name'))
            file_id.write( '{0:<50} {1}\n'.format('mask_file = {0}'.format(mask_file), '# mask file name (ignore all alignment within transcripts in this file) or NONE'))
            for i in range(len(alignment_dataset_id_list)):
                # set the alignment software
                alignment_dataset_id = alignment_dataset_id_list[i]
                if alignment_dataset_id.startswith(xlib.get_star_code()):
                    alignment_software = xlib.get_star_code()
                elif alignment_dataset_id.startswith(xlib.get_tophat_code()):
                    alignment_software = xlib.get_tophat_code()
                # write the alignment dataset section
                file_id.write( '\n')
                if i == 0:
                    file_id.write( '{0}\n'.format('# This section has the information of the first alignment dataset.'))
                file_id.write( '{0}\n'.format('[alignment-dataset-{0}]'.format(i + 1)))
                file_id.write( '{0:<50} {1}\n'.format('alignment_software = {0}'.format(alignment_software), '# alignment software: {0}'.format(get_alignment_software_code_list_text())))
                file_id.write( '{0:<50} {1}\n'.format('alignment_dataset_id = {0}'.format(alignment_dataset_id), '# alignment dataset identification'))
                if i == 0:
                    file_id.write( '\n')
                    file_id.write( '{0}\n'.format('# If there are more alignment datasets, you have to repeat the section alignment-dataset-1 with the data of each dataset.'))
                    file_id.write( '{0}\n'.format('# The section identification has to be alignment-dataset-n (n is an integer not repeated)'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information to set the Cufflinks parameters'))
            file_id.write( '{0}\n'.format('[Cufflinks parameters]'))
            file_id.write( '{0:<50} {1}\n'.format('threads = 4', '# number of threads for use'))
            file_id.write( '{0:<50} {1}\n'.format('library_type = FR-UNSTRANDED', '# library type: {0}'.format(get_library_type_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('other_parameters = NONE', '# additional parameters to the previous ones or NONE'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information to set the Cuffmerge parameters'))
            file_id.write( '{0}\n'.format('[Cuffmerge parameters]'))
            file_id.write( '{0:<50} {1}\n'.format('min_isoform_fraction = 0.05', '# discard isoforms with abundance below this ((0.0 <= min_isoform_fraction <= 1.0))'))
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_cufflinks_cuffmerge_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_cufflinks_cuffmerge_process(cluster_name, log, function=None):
    '''
    Run a Cufflinks-Cuffmerge process.
    '''

    # initialize the control variable
    OK = True

    # get the Cufflinks-Cuffmerge option dictionary
    cufflinks_cuffmerge_option_dict = xlib.get_option_dict(get_cufflinks_cuffmerge_config_file())

    # get the experiment identification
    experiment_id = cufflinks_cuffmerge_option_dict['identification']['experiment_id']

    # warn that the log window does not have to be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # check the Cufflinks-Cuffmerge config file
    log.write(f'{xlib.get_separator()}\n')
    log.write('Checking the {0} config file ...\n'.format(xlib.get_cufflinks_cuffmerge_name()))
    (OK, error_list) = check_cufflinks_cuffmerge_config_file(strict=True)
    if OK:
        log.write('The file is OK.\n')
    else:
        log.write('*** ERROR: The config file is not valid.\n')
        log.write('Please correct this file or recreate the config files.\n')

    # create the SSH client connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SSH client ...\n')
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name)
        if OK:
            log.write('The SSH client is connected.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # create the SSH transport connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SSH transport ...\n')
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name)
        if OK:
            log.write('The SSH transport is connected.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # create the SFTP client 
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SFTP client ...\n')
        sftp_client = xssh.create_sftp_client(ssh_transport)
        log.write('The SFTP client is connected.\n')

    # warn that the requirements are being verified 
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Checking process requirements ...\n')

    # check the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name)
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # check Cufflinks is installed
    if OK:
        (OK, error_list, is_installed) = xbioinfoapp.is_installed_bioconda_package(xlib.get_cufflinks_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_installed:
                log.write('*** ERROR: {0} is not installed.\n'.format(xlib.get_cufflinks_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} installation could not be performed.\n'.format(xlib.get_cufflinks_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_cufflinks_cuffmerge_code())
        command = f'mkdir --parents {current_run_dir}'
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Cufflinks-Cuffmerge process script
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process script {0} ...\n'.format(get_cufflinks_cuffmerge_process_script()))
        (OK, error_list) = build_cufflinks_cuffmerge_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Cufflinks-Cuffmerge process script to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(get_cufflinks_cuffmerge_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_cufflinks_cuffmerge_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_cufflinks_cuffmerge_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Cufflinks-Cuffmerge process script in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_cufflinks_cuffmerge_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_cufflinks_cuffmerge_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Cufflinks-Cuffmerge process starter
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process starter {0} ...\n'.format(get_cufflinks_cuffmerge_process_starter()))
        (OK, error_list) = build_cufflinks_cuffmerge_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Cufflinks-Cuffmerge process starter to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(get_cufflinks_cuffmerge_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_cufflinks_cuffmerge_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_cufflinks_cuffmerge_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Cufflinks-Cuffmerge process starter in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_cufflinks_cuffmerge_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_cufflinks_cuffmerge_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # submit the Cufflinks-Cuffmerge process
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_cufflinks_cuffmerge_process_starter())))
        OK = xssh.submit_script(cluster_name, ssh_client, current_run_dir, os.path.basename(get_cufflinks_cuffmerge_process_starter()), log)

    # close the SSH transport connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Closing the SSH transport connection ...\n')
        xssh.close_ssh_transport_connection(ssh_transport)
        log.write('The connection is closed.\n')

    # close the SSH client connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write(f'{xlib.get_separator()}\n')
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def check_cufflinks_cuffmerge_config_file(strict):
    '''
    Check the Cufflinks-Cuffmerge config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        cufflinks_cuffmerge_option_dict = xlib.get_option_dict(get_cufflinks_cuffmerge_config_file())
    except Exception as e:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in cufflinks_cuffmerge_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = cufflinks_cuffmerge_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "reference_dataset_id"
            reference_dataset_id = cufflinks_cuffmerge_option_dict.get('identification', {}).get('reference_dataset_id', not_found)
            if reference_dataset_id == not_found:
                error_list.append('*** ERROR: the key "reference_dataset_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "reference_file"
            reference_file = cufflinks_cuffmerge_option_dict.get('identification', {}).get('reference_file', not_found)
            if reference_file == not_found:
                error_list.append('*** ERROR: the key "reference_file" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "gtf_guide"
            gtf_guide = cufflinks_cuffmerge_option_dict.get('identification', {}).get('gtf_guide', not_found)
            if gtf_guide == not_found:
                error_list.append('*** ERROR: the key "gtf_guide" is not found in the section "identification".')
                OK = False
            elif os.path.splitext(gtf_guide)[1] not in ['.gtf', '.gff']:
                error_list.append('*** ERROR: the key "gtf_guide" has to be a file name with .gtf/.gff extension.')
                OK = False

            # check section "identification" - key "mask_file"
            mask_file = cufflinks_cuffmerge_option_dict.get('identification', {}).get('mask_file', not_found)
            if mask_file == not_found:
                error_list.append('*** ERROR: the key "mask_file" is not found in the section "identification".')
                OK = False
            elif mask_file != 'NONE' and os.path.splitext(mask_file)[1] not in ['.gtf', '.gff']:
                error_list.append('*** ERROR: the key "mask_file" has to be a file name with .gtf/.gff extension or NONE.')
                OK = False

        # check section "alignment-dataset-1"
        if 'alignment-dataset-1' not in sections_list:
            error_list.append('*** ERROR: the section "alignment-dataset-1" is not found.')
            OK = False

        # check section "alignment-dataset-2"
        if 'alignment-dataset-2' not in sections_list:
            error_list.append('*** ERROR: the section "alignment-dataset-2" is not found.')
            OK = False

        # check all sections "alignment-dataset-n"
        for section in sections_list:

            if section not in ['identification', 'Cufflinks parameters', 'Cuffmerge parameters']:

                # check than the section identification is like alignment-dataset-n 
                if not re.match('^alignment-dataset-[0-9]+$', section):
                    error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                    OK = False

                else:

                    # check section "alignment-dataset-n" - key "alignment_software"
                    alignment_software = cufflinks_cuffmerge_option_dict.get(section, {}).get('alignment_software', not_found)
                    if alignment_software == not_found:
                        error_list.append('*** ERROR: the key "alignment_software" is not found in the section "{0}".'.format(section))
                        OK = False
                    elif not xlib.check_code(alignment_software, get_alignment_software_code_list(), case_sensitive=False):
                        error_list.append('*** ERROR: the key "alignment_software" has to be {0}.'.format(get_alignment_software_code_list_text()))
                        OK = False

                    # check section "alignment-dataset-n" - key "alignment_dataset_id"
                    alignment_dataset_id = cufflinks_cuffmerge_option_dict.get(section, {}).get('alignment_dataset_id', not_found)
                    if alignment_dataset_id == not_found:
                        error_list.append('*** ERROR: the key "alignment_dataset_id" is not found in the section "{0}".'.format(section))
                        OK = False
                    elif not xlib.check_startswith(alignment_dataset_id, get_alignment_software_code_list(), case_sensitive=True):
                        error_list.append('*** ERROR: the key "alignment_dataset_id" has to start with {0}.'.format(get_alignment_software_code_list_text()))
                        OK = False

        # check section "Cufflinks parameters"
        if 'Cufflinks parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Cufflinks parameters" is not found.')
            OK = False
        else:

            # check section "Cufflinks parameters" - key "threads"
            threads = cufflinks_cuffmerge_option_dict.get('Cufflinks parameters', {}).get('threads', not_found)
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "Cufflinks parameters".')
                OK = False
            elif not xlib.check_int(threads, minimum=1):
                error_list.append('*** ERROR: the key "threads" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cufflinks parameters" - key "library_type"
            library_type = cufflinks_cuffmerge_option_dict.get('Cufflinks parameters', {}).get('library_type', not_found).lower()
            if library_type == not_found:
                error_list.append('*** ERROR: the key "library_type" is not found in the section "Cufflinks parameters".')
                OK = False
            elif not xlib.check_code(library_type, get_library_type_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "library_type" has to be {0}.'.format(get_library_type_code_list_text()))
                OK = False

            # check section "Cufflinks parameters" - key "other_parameters"
            not_allowed_parameters_list = ['no-update-check', 'num-threads', 'GTF-guide', 'mask-file', 'library-type', 'library-norm-method', 'output-dir']
            other_parameters = cufflinks_cuffmerge_option_dict.get('Cufflinks parameters', {}).get('other_parameters', not_found)
            if other_parameters == not_found:
                error_list.append('*** ERROR: the key "other_parameters" is not found in the section "Cufflinks parameters".')
                OK = False
            elif other_parameters.upper() != 'NONE':
                (OK, error_list2) = xlib.check_parameter_list(other_parameters, "other_parameters", not_allowed_parameters_list)
                error_list = error_list + error_list2

        # check section "Cuffmerge parameters"
        if 'Cuffmerge parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Cuffmerge parameters" is not found.')
            OK = False
        else:

            # check section "Cuffmerge parameters" - key "min_isoform_fraction"
            min_isoform_fraction = cufflinks_cuffmerge_option_dict.get('Cuffmerge parameters', {}).get('min_isoform_fraction', not_found)
            is_ok_min_isoform_fraction = False
            if min_isoform_fraction == not_found:
                error_list.append('*** ERROR: the key "min_isoform_fraction" is not found in the section "Cuffmerge parameters".')
                OK = False
            elif not xlib.check_float(min_isoform_fraction, minimum=0., maximum=1.):
                error_list.append('*** ERROR: the key "min_isoform_fraction" has to be a float number between 0.0 and 1.0.')
                OK = False

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_cufflinks_cuffmerge_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_cufflinks_cuffmerge_process_script(cluster_name, current_run_dir):
    '''
    Build the current Cufflinks-Cuffmerge process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the Cufflinks-Cuffmerge option dictionary
    cufflinks_cuffmerge_option_dict = xlib.get_option_dict(get_cufflinks_cuffmerge_config_file())

    # get the options
    experiment_id = cufflinks_cuffmerge_option_dict['identification']['experiment_id']
    reference_dataset_id = cufflinks_cuffmerge_option_dict['identification']['reference_dataset_id']
    reference_file = cufflinks_cuffmerge_option_dict['identification']['reference_file']
    gtf_guide = cufflinks_cuffmerge_option_dict['identification']['gtf_guide']
    mask_file = cufflinks_cuffmerge_option_dict['identification']['mask_file']
    threads = cufflinks_cuffmerge_option_dict['Cufflinks parameters']['threads']
    library_type = cufflinks_cuffmerge_option_dict['Cufflinks parameters']['library_type']
    other_parameters = cufflinks_cuffmerge_option_dict['Cufflinks parameters']['other_parameters']
    min_isoform_fraction = cufflinks_cuffmerge_option_dict['Cuffmerge parameters']['min_isoform_fraction']

    # get the sections list
    sections_list = []
    for section in cufflinks_cuffmerge_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build alignment dataset identification list
    alignment_software_list = []
    alignment_dataset_id_list = []
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^alignment-dataset-[0-9]+$', section):
            alignment_software_list.append(cufflinks_cuffmerge_option_dict[section]['alignment_software'])
            alignment_dataset_id_list.append(cufflinks_cuffmerge_option_dict[section]['alignment_dataset_id'])

    # set the path of the file with the alignment dataset identification list
    alignment_dataset_id_list_file = '{0}/alignment_dataset_id_list.txt'.format(current_run_dir)

    # set the reference file path
    reference_file = xlib.get_cluster_reference_file(reference_dataset_id, reference_file)

    # set the gtf guide file path
    gtf_guide = xlib.get_cluster_reference_file(reference_dataset_id, gtf_guide)

    # set the mask file path
    if mask_file.upper() != 'NONE':
        mask_file = xlib.get_cluster_reference_file(reference_dataset_id, mask_file)

    # set the path of the file with the Cufflinks output gft list
    cufflinks_output_gft_list_file = '{0}/cufflinks_output_gtf_list.txt'.format(current_run_dir)

    # write the Cufflinks-Cuffmerge process script
    try:
        if not os.path.exists(os.path.dirname(get_cufflinks_cuffmerge_process_script())):
            os.makedirs(os.path.dirname(get_cufflinks_cuffmerge_process_script()))
        with open(get_cufflinks_cuffmerge_process_script(), mode='w', encoding='iso-8859-1', newline='\n') as script_file_id:
            script_file_id.write( '#!/bin/bash\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'SEP="#########################################"\n')
            script_file_id.write( 'export HOST_IP=`curl --silent checkip.amazonaws.com`\n')
            script_file_id.write( 'export HOST_ADDRESS="ec2-${HOST_IP//./-}-compute-1.amazonaws.com"\n')
            script_file_id.write( '{0}\n'.format('CUFFLINKS_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_cufflinks_bioconda_code())))
            script_file_id.write( '{0}\n'.format('export PATH=$CUFFLINKS_PATH:$PATH'))
            script_file_id.write( '{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            script_file_id.write( '{0}\n'.format('source activate {0}'.format(xlib.get_cufflinks_bioconda_code())))
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('STATUS_DIR={0}'.format(xlib.get_status_dir(current_run_dir))))
            script_file_id.write( '{0}\n'.format('SCRIPT_STATUS_OK={0}'.format(xlib.get_status_ok(current_run_dir))))
            script_file_id.write( '{0}\n'.format('SCRIPT_STATUS_WRONG={0}'.format(xlib.get_status_wrong(current_run_dir))))
            script_file_id.write( '{0}\n'.format('mkdir --parents $STATUS_DIR'))
            script_file_id.write( '{0}\n'.format('if [ -f $SCRIPT_STATUS_OK ]; then rm $SCRIPT_STATUS_OK; fi'))
            script_file_id.write( '{0}\n'.format('if [ -f $SCRIPT_STATUS_WRONG ]; then rm $SCRIPT_STATUS_WRONG; fi'))
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function init\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    INIT_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "Script started at $FORMATTED_INIT_DATETIME+00:00."\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write(f'    echo "CLUSTER: {cluster_name}"\n')
            script_file_id.write(f'    echo "HOST_IP: $HOST_IP - HOST_ADDRESS: $HOST_ADDRESS"\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function create_alignment_dataset_list_file'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Creation of alignment dataset list file ..."'))
            script_file_id.write( '{0}\n'.format('    touch {0}'.format(alignment_dataset_id_list_file)))
            for i in range(len(alignment_dataset_id_list)):
                script_file_id.write( '{0}\n'.format('    echo "{0}" >> {1}'.format(alignment_dataset_id_list[i], alignment_dataset_id_list_file)))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function run_cufflinks_process'))
            script_file_id.write( '{\n')
            for i in range(len(alignment_dataset_id_list)):
                script_file_id.write( '{0}\n'.format('    mkdir --parents {0}/{1}'.format(current_run_dir, alignment_dataset_id_list[i])))
                script_file_id.write( '{0}\n'.format('    cd {0}/{1}'.format(current_run_dir, alignment_dataset_id_list[i])))
                script_file_id.write( '    echo "$SEP"\n')
                if alignment_software_list[i] == xlib.get_star_code():
                    alignment_file = '{0}/starAligned.sortedByCoord.out.bam'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, alignment_dataset_id_list[i]))
                elif alignment_software_list[i] == xlib.get_tophat_code():
                    alignment_file = '{0}/accepted_hits.bam'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, alignment_dataset_id_list[i]))
                script_file_id.write( '{0}\n'.format('    echo "Cufflinks process for alignment dataset {0}..."'.format(alignment_dataset_id_list[i])))
                script_file_id.write( '{0}\n'.format('    /usr/bin/time \\'))
                script_file_id.write( '{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
                script_file_id.write( '{0}\n'.format('        cufflinks \\'))
                script_file_id.write( '{0}\n'.format('            --no-update-check \\'))
                script_file_id.write( '{0}\n'.format('            --num-threads {0} \\'.format(threads)))
                script_file_id.write( '{0}\n'.format('            --GTF-guide {0} \\'.format(gtf_guide)))
                if mask_file.upper() != 'NONE':
                    script_file_id.write( '{0}\n'.format('            --mask-file {0} \\'.format(mask_file)))
                script_file_id.write( '{0}\n'.format('            --library-type {0} \\'.format(library_type)))
                if other_parameters.upper() != 'NONE':
                    parameter_list = [x.strip() for x in other_parameters.split(';')]
                    for j in range(len(parameter_list)):
                        if parameter_list[j].find('=') > 0:
                            pattern = r'^--(.+)=(.+)$'
                            mo = re.search(pattern, parameter_list[j])
                            parameter_name = mo.group(1).strip()
                            parameter_value = mo.group(2).strip()
                            script_file_id.write( '{0}\n'.format('            --{0} {1} \\'.format(parameter_name, parameter_value)))
                        else:
                            pattern = r'^--(.+)$'
                            mo = re.search(pattern, parameter_list[j])
                            parameter_name = mo.group(1).strip()
                            script_file_id.write( '{0}\n'.format('            --{0} \\'.format(parameter_name)))
                script_file_id.write( '{0}\n'.format('            --output-dir {0}/{1} \\'.format(current_run_dir, alignment_dataset_id_list[i])))
                script_file_id.write( '{0}\n'.format('            {0}'.format(alignment_file)))
                script_file_id.write( '{0}\n'.format('    RC=$?'))
                script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error cufflinks $RC; fi'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function create_cufflinks_output_gtf_list_file'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Create Cufflinks output gtf list file ..."'))
            script_file_id.write( '{0}\n'.format('    touch {0}'.format(cufflinks_output_gft_list_file)))
            for alignment_dataset_id in alignment_dataset_id_list:
                script_file_id.write( '{0}\n'.format('    ls {0}/{1}/transcripts.gtf >> {2}'.format(current_run_dir, alignment_dataset_id, cufflinks_output_gft_list_file)))
                script_file_id.write( '{0}\n'.format('    RC=$?'))
                script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error ls $RC; fi'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function run_cuffmerge_process'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Cuffmerge process ..."'))
            script_file_id.write( '{0}\n'.format('    /usr/bin/time \\'))
            script_file_id.write( '{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            script_file_id.write( '{0}\n'.format('        cuffmerge \\'))
            script_file_id.write( '{0}\n'.format('            --num-threads {0} \\'.format(threads)))
            script_file_id.write( '{0}\n'.format('            --ref-sequence {0} \\'.format(reference_file)))
            script_file_id.write( '{0}\n'.format('            --ref-gtf {0} \\'.format(gtf_guide)))
            script_file_id.write( '{0}\n'.format('            --min-isoform-fraction {0} \\'.format(min_isoform_fraction)))
            script_file_id.write( '{0}\n'.format('            --output-dir {0} \\'.format(current_run_dir)))
            script_file_id.write( '{0}\n'.format('            {0}'.format(cufflinks_output_gft_list_file)))
            script_file_id.write( '{0}\n'.format('    RC=$?'))
            script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error cuffmerge $RC; fi'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function end'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            script_file_id.write( '{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            script_file_id.write( '{0}\n'.format('    calculate_duration'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Script ended OK at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            script_file_id.write( '{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_cufflinks_cuffmerge_name())))
            script_file_id.write( '{0}\n'.format('    MESSAGE="{0}"'.format(xlib.get_mail_message_ok(xlib.get_cufflinks_cuffmerge_name(), cluster_name))))
            script_file_id.write( '    mail --append "Content-type: text/html;" --append "FROM:root@NGScloud2" --subject="$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"\n')
            script_file_id.write( '{0}\n'.format('    touch $SCRIPT_STATUS_OK'))
            script_file_id.write( '{0}\n'.format('    exit 0'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function manage_error'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            script_file_id.write( '{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            script_file_id.write( '{0}\n'.format('    calculate_duration'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "ERROR: $1 returned error $2"'))
            script_file_id.write( '{0}\n'.format('    echo "Script ended WRONG at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            script_file_id.write( '{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_cufflinks_cuffmerge_name())))
            script_file_id.write( '{0}\n'.format('    MESSAGE="{0}"'.format(xlib.get_mail_message_wrong(xlib.get_cufflinks_cuffmerge_name(), cluster_name))))
            script_file_id.write( '    mail --append "Content-type: text/html;" --append "FROM:root@NGScloud2" --subject="$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"\n')
            script_file_id.write( '{0}\n'.format('    touch $SCRIPT_STATUS_WRONG'))
            script_file_id.write( '{0}\n'.format('    exit 3'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function calculate_duration\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    DURATION=`expr $END_DATETIME - $INIT_DATETIME`\n')
            script_file_id.write( '    HH=`expr $DURATION / 3600`\n')
            script_file_id.write( '    MM=`expr $DURATION % 3600 / 60`\n')
            script_file_id.write( '    SS=`expr $DURATION % 60`\n')
            script_file_id.write( '    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'init\n')
            script_file_id.write( '{0}\n'.format('create_alignment_dataset_list_file'))
            script_file_id.write( '{0}\n'.format('run_cufflinks_process'))
            script_file_id.write( '{0}\n'.format('create_cufflinks_output_gtf_list_file'))
            script_file_id.write( '{0}\n'.format('run_cuffmerge_process'))
            script_file_id.write( 'end\n')
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_cufflinks_cuffmerge_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_cufflinks_cuffmerge_process_starter(current_run_dir):
    '''
    Build the starter of the current Cufflinks-Cuffmerge process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Cufflinks-Cuffmerge process starter
    try:
        if not os.path.exists(os.path.dirname(get_cufflinks_cuffmerge_process_starter())):
            os.makedirs(os.path.dirname(get_cufflinks_cuffmerge_process_starter()))
        with open(get_cufflinks_cuffmerge_process_starter(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '{0}\n'.format('#!/bin/bash'))
            file_id.write( '{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write( '{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_cufflinks_cuffmerge_process_script()), xlib.get_cluster_log_file())))
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_cufflinks_cuffmerge_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_cufflinks_cuffmerge_config_file():
    '''
    Get the Cufflinks-Cuffmerge config file path.
    '''

    # assign the Cufflinks-Cuffmerge config file path
    cufflinks_cuffmerge_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_cufflinks_cuffmerge_code())

    # return the Cufflinks-Cuffmerge config file path
    return cufflinks_cuffmerge_config_file

#-------------------------------------------------------------------------------

def get_cufflinks_cuffmerge_process_script():
    '''
    Get the Cufflinks-Cuffmerge process script path in the local computer.
    '''

    # assign the Cufflinks-Cuffmerge script path
    cufflinks_cuffmerge_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_cufflinks_cuffmerge_code())

    # return the Cufflinks-Cuffmerge script path
    return cufflinks_cuffmerge_process_script

#-------------------------------------------------------------------------------

def get_cufflinks_cuffmerge_process_starter():
    '''
    Get the Cufflinks-Cuffmerge process starter path in the local computer.
    '''

    # assign the Cufflinks-Cuffmerge process starter path
    cufflinks_cuffmerge_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_cufflinks_cuffmerge_code())

    # return the Cufflinks_Cuffmerge starter path
    return cufflinks_cuffmerge_process_starter

#-------------------------------------------------------------------------------

def create_cuffquant_config_file(experiment_id='exp001', reference_dataset_id='Athaliana', mask_file='NONE', alignment_dataset_id_list=['star-170101-235959','tophat-170101-235959'], assembly_dataset_id='cufflnkmrg-170101-235959'):
    '''
    Create Cuffquant config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # set the assembly software
    if assembly_dataset_id.startswith(xlib.get_cufflinks_cuffmerge_code()):
        assembly_software = xlib.get_cufflinks_cuffmerge_code()

    # create the Cuffquant config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_cuffquant_config_file())):
            os.makedirs(os.path.dirname(get_cuffquant_config_file()))
        with open(get_cuffquant_config_file(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# The reference and GTF files have to be located in the cluster directory {0}/experiment_id/reference_dataset_id'.format(xlib.get_cluster_reference_dir())))
            file_id.write( '{0}\n'.format('# The experiment_id, reference_dataset_id, mask_file and assembly_dataset_id names are fixed in the identification section.'))
            file_id.write( '{0}\n'.format('# The alignment files have to be located in the cluster directory {0}/experiment_id/alignment_dataset_id'.format(xlib.get_cluster_result_dir())))
            file_id.write( '{0}\n'.format('# The assembly files have to be located in the cluster directory {0}/experiment_id/assembly_dataset_id'.format(xlib.get_cluster_result_dir())))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# You can consult the parameters of Cuffquant and their meaning in http://cole-trapnell-lab.github.io/cufflinks/.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# In section "Cuffquant parameters", the key "other_parameters" allows you to input additional parameters in the format:'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('#    other_parameters = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# parameter-i is a parameter name of Cuffquant and value-i a valid value of parameter-i, e.g.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('#    other_parameters = --multi-read-correct; --no-length-correction'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information identifies the experiment.'))
            file_id.write( '{0}\n'.format('[identification]'))
            file_id.write( '{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write( '{0:<50} {1}\n'.format('reference_dataset_id = {0}'.format(reference_dataset_id), '# reference dataset identification'))
            file_id.write( '{0:<50} {1}\n'.format('mask_file = {0}'.format(mask_file), '# mask file name (ignore all alignment within transcripts in this file) or NONE'))
            file_id.write( '{0:<50} {1}\n'.format('assembly_software = {0}'.format(assembly_software), '# assembly software: {0})'.format(get_assembly_software_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('assembly_dataset_id = {0}'.format(assembly_dataset_id), '# assembly dataset identification'))
            for i in range(len(alignment_dataset_id_list)):
                # set the alignment software
                alignment_dataset_id = alignment_dataset_id_list[i]
                if alignment_dataset_id.startswith(xlib.get_star_code()):
                    alignment_software = xlib.get_star_code()
                elif alignment_dataset_id.startswith(xlib.get_tophat_code()):
                    alignment_software = xlib.get_tophat_code()
                # write the alignment dataset section
                file_id.write( '\n')
                if i == 0:
                    file_id.write( '{0}\n'.format('# This section has the information of the first alignment dataset.'))
                file_id.write( '{0}\n'.format('[alignment-dataset-{0}]'.format(i + 1)))
                file_id.write( '{0:<50} {1}\n'.format('alignment_software = {0}'.format(alignment_software), '# alignment software: {0}'.format(get_alignment_software_code_list_text())))
                file_id.write( '{0:<50} {1}\n'.format('alignment_dataset_id = {0}'.format(alignment_dataset_id), '# alignment dataset identification'))
                file_id.write( '{0:<50} {1}\n'.format('group_label = individual_1', '# condition label (replicates of a condition should share the same label)'))
                if i == 0:
                    file_id.write( '\n')
                    file_id.write( '{0}\n'.format('# If there are more alignment datasets, you have to repeat the section alignment-dataset-1 with the data of each dataset.'))
                    file_id.write( '{0}\n'.format('# The section identification has to be alignment-dataset-n (n is an integer not repeated)'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information to set the Cuffquant parameters'))
            file_id.write( '{0}\n'.format('[Cuffquant parameters]'))
            file_id.write( '{0:<50} {1}\n'.format('threads = 4', '# number of threads for use'))
            file_id.write( '{0:<50} {1}\n'.format('library_type = FR-UNSTRANDED', '# library type: {0}'.format(get_library_type_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('frag_len_mean = 200', '# expected (mean) fragment length'))
            file_id.write( '{0:<50} {1}\n'.format('frag_len_std_dev = 80', '# standard deviation for the distribution on fragment lengths'))
            file_id.write( '{0:<50} {1}\n'.format('max_mle_iterations = 5000', '# number of iterations allowed during maximum likelihood estimation of abundances'))
            file_id.write( '{0:<50} {1}\n'.format('max_bundle_frags = 1000000', '# maximum number of fragments a locus may have before being skipped'))
            file_id.write( '{0:<50} {1}\n'.format('other_parameters = NONE', '# additional parameters to the previous ones or NONE'))
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_cufflinks_cuffmerge_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_cuffquant_process(cluster_name, log, function=None):
    '''
    Run a Cuffquant process.
    '''

    # initialize the control variable
    OK = True

    # get the Cuffquant option dictionary
    cuffquant_option_dict = xlib.get_option_dict(get_cuffquant_config_file())

    # get the experiment identification
    experiment_id = cuffquant_option_dict['identification']['experiment_id']

    # warn that the log window does not have to be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # check the Cuffquant config file
    log.write(f'{xlib.get_separator()}\n')
    log.write('Checking the {0} config file ...\n'.format(xlib.get_cuffquant_name()))
    (OK, error_list) = check_cuffquant_config_file(strict=True)
    if OK:
        log.write('The file is OK.\n')
    else:
        log.write('*** ERROR: The config file is not valid.\n')
        log.write('Please correct this file or recreate the config files.\n')

    # create the SSH client connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SSH client ...\n')
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name)
        if OK:
            log.write('The SSH client is connected.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # create the SSH transport connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SSH transport ...\n')
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name)
        if OK:
            log.write('The SSH transport is connected.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # create the SFTP client 
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SFTP client ...\n')
        sftp_client = xssh.create_sftp_client(ssh_transport)
        log.write('The SFTP client is connected.\n')

    # warn that the requirements are being verified 
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Checking process requirements ...\n')

    # check the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name)
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # check Cufflinks is installed
    if OK:
        (OK, error_list, is_installed) = xbioinfoapp.is_installed_bioconda_package(xlib.get_cufflinks_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_installed:
                log.write('*** ERROR: {0} is not installed.\n'.format(xlib.get_cufflinks_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} installation could not be performed.\n'.format(xlib.get_cufflinks_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_cuffquant_code())
        command = f'mkdir --parents {current_run_dir}'
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Cuffquant process script
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process script {0} ...\n'.format(get_cuffquant_process_script()))
        (OK, error_list) = build_cuffquant_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Cuffquant process script to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(get_cuffquant_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_cuffquant_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_cuffquant_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Cuffquant process script in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_cuffquant_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_cuffquant_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Cuffquant process starter
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process starter {0} ...\n'.format(get_cuffquant_process_starter()))
        (OK, error_list) = build_cuffquant_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Cuffquant process starter to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(get_cuffquant_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_cuffquant_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_cuffquant_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Cuffquant process starter in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_cuffquant_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_cuffquant_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # submit the Cuffquant process
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_cuffquant_process_starter())))
        OK = xssh.submit_script(cluster_name, ssh_client, current_run_dir, os.path.basename(get_cuffquant_process_starter()), log)

    # close the SSH transport connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Closing the SSH transport connection ...\n')
        xssh.close_ssh_transport_connection(ssh_transport)
        log.write('The connection is closed.\n')

    # close the SSH client connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write(f'{xlib.get_separator()}\n')
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def check_cuffquant_config_file(strict):
    '''
    Check the Cuffquant config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        cuffquant_option_dict = xlib.get_option_dict(get_cuffquant_config_file())
    except Exception as e:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in cuffquant_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = cuffquant_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "reference_dataset_id"
            reference_dataset_id = cuffquant_option_dict.get('identification', {}).get('reference_dataset_id', not_found)
            if reference_dataset_id == not_found:
                error_list.append('*** ERROR: the key "reference_dataset_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "mask_file"
            mask_file = cuffquant_option_dict.get('identification', {}).get('mask_file', not_found)
            if mask_file == not_found:
                error_list.append('*** ERROR: the key "mask_file" is not found in the section "identification".')
                OK = False
            elif mask_file != 'NONE' and os.path.splitext(mask_file)[1] not in ['.gtf', '.gff']:
                error_list.append('*** ERROR: the key "mask_file" has to be a file name with .gtf/.gff extension or NONE.')
                OK = False

            # check section "identification" - key "assembly_software"
            assembly_software = cuffquant_option_dict.get('identification', {}).get('assembly_software', not_found)
            if assembly_software == not_found:
                error_list.append('*** ERROR: the key "assembly_software" is not found in the section "identification".')
                OK = False
            elif not xlib.check_code(assembly_software, get_assembly_software_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "assembly_software" has to be {0}.'.format(get_assembly_software_code_list_text()))
                OK = False

            # check section "identification" - key "assembly_dataset_id"
            assembly_dataset_id = cuffquant_option_dict.get('identification', {}).get('assembly_dataset_id', not_found)
            if assembly_dataset_id == not_found:
                error_list.append('*** ERROR: the key "assembly_dataset_id" is not found in the section "identification".')
                OK = False
            elif not xlib.check_startswith(assembly_dataset_id, get_assembly_software_code_list(), case_sensitive=True):
                error_list.append('*** ERROR: the key "assembly_dataset_id" has to start with {0}.'.format(get_assembly_software_code_list_text()))
                OK = False

        # check section "alignment-dataset-1"
        if 'alignment-dataset-1' not in sections_list:
            error_list.append('*** ERROR: the section "alignment-dataset-1" is not found.')
            OK = False

        # check all sections "alignment-dataset-n"
        for section in sections_list:

            if section not in ['identification', 'Cuffquant parameters']:

                # check than the section identification is like alignment-dataset-n 
                if not re.match('^alignment-dataset-[0-9]+$', section):
                    error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                    OK = False

                else:

                    # check section "alignment-dataset-n" - key "alignment_software"
                    alignment_software = cuffquant_option_dict.get(section, {}).get('alignment_software', not_found)
                    if alignment_software == not_found:
                        error_list.append('*** ERROR: the key "alignment_software" is not found in the section "{0}".'.format(section))
                        OK = False
                    elif not xlib.check_code(alignment_software, get_alignment_software_code_list(), case_sensitive=False):
                        error_list.append('*** ERROR: the key "alignment_software" has to be {0}.'.format(get_alignment_software_code_list_text()))
                        OK = False

                    # check section "alignment-dataset-n" - key "alignment_dataset_id"
                    alignment_dataset_id = cuffquant_option_dict.get(section, {}).get('alignment_dataset_id', not_found)
                    if alignment_dataset_id == not_found:
                        error_list.append('*** ERROR: the key "alignment_dataset_id" is not found in the section "{0}".'.format(section))
                        OK = False
                    elif not xlib.check_startswith(alignment_dataset_id, get_alignment_software_code_list(), case_sensitive=True):
                        error_list.append('*** ERROR: the key "alignment_dataset_id" has to start with {0}.'.format(get_alignment_software_code_list_text()))
                        OK = False

                    # check section "alignment-dataset-n" - key "group_label"
                    group_label = cuffquant_option_dict.get(section, {}).get('group_label', not_found)
                    if group_label == not_found:
                        error_list.append('*** ERROR: the key "group_label" is not found in the section "{0}".'.format(section))
                        OK = False

        # check section "Cuffquant parameters"
        if 'Cuffquant parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Cuffquant parameters" is not found.')
            OK = False
        else:

            # check section "Cuffquant parameters" - key "threads"
            threads = cuffquant_option_dict.get('Cuffquant parameters', {}).get('threads', not_found)
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_int(threads, minimum=1):
                error_list.append('*** ERROR: the key "threads" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffquant parameters" - key "library_type"
            library_type = cuffquant_option_dict.get('Cuffquant parameters', {}).get('library_type', not_found).lower()
            if library_type == not_found:
                error_list.append('*** ERROR: the key "library_type" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_code(library_type, get_library_type_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "library_type" has to be {0}.'.format(get_library_type_code_list_text()))
                OK = False

            # check section "Cuffquant parameters" - key "frag_len_mean"
            frag_len_mean = cuffquant_option_dict.get('Cuffquant parameters', {}).get('frag_len_mean', not_found)
            if frag_len_mean == not_found:
                error_list.append('*** ERROR: the key "frag_len_mean" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_int(frag_len_mean, minimum=1):
                error_list.append('*** ERROR: the key "frag_len_mean" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffquant parameters" - key "frag_len_std_dev"
            frag_len_std_dev = cuffquant_option_dict.get('Cuffquant parameters', {}).get('frag_len_std_dev', not_found)
            if frag_len_std_dev == not_found:
                error_list.append('*** ERROR: the key "frag_len_std_dev" is not found in the section "Cuffquant parameters".')
                OK = False
            elif not xlib.check_int(frag_len_std_dev, minimum=1):
                error_list.append('*** ERROR: the key "frag_len_std_dev" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffquant parameters" - key "max_mle_iterations"
            max_mle_iterations = cuffquant_option_dict.get('Cuffquant parameters', {}).get('max_mle_iterations', not_found)
            if max_mle_iterations == not_found:
                error_list.append('*** ERROR: the key "max_mle_iterations" is not found in the section "Cuffquant parameters".')
                OK = False
            elif not xlib.check_int(max_mle_iterations, minimum=1):
                error_list.append('*** ERROR: the key "max_mle_iterations" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffquant parameters" - key "max_bundle_frags"
            max_bundle_frags = cuffquant_option_dict.get('Cuffquant parameters', {}).get('max_bundle_frags', not_found)
            if max_bundle_frags == not_found:
                error_list.append('*** ERROR: the key "max_bundle_frags" is not found in the section "Cuffquant parameters".')
                OK = False
            elif not xlib.check_int(max_bundle_frags, minimum=1):
                error_list.append('*** ERROR: the key "max_bundle_frags" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffquant parameters" - key "other_parameters"
            not_allowed_parameters_list = ['no-update-check', 'num-threads', 'mask-file', 'library_type', 'output-dir', 'frag-len-mean', 'frag-len-std-dev', 'max-mle-iterations', 'max-bundle-frags']
            other_parameters = cuffquant_option_dict.get('Cuffquant parameters', {}).get('other_parameters', not_found)
            if other_parameters == not_found:
                error_list.append('*** ERROR: the key "other_parameters" is not found in the section "Cuffquant parameters".')
                OK = False
            elif other_parameters.upper() != 'NONE':
                (OK, error_list2) = xlib.check_parameter_list(other_parameters, "other_parameters", not_allowed_parameters_list)
                error_list = error_list + error_list2

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_cuffquant_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_cuffquant_process_script(cluster_name, current_run_dir):
    '''
    Build the current Cuffquant process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the Cuffquant option dictionary
    cuffquant_option_dict = xlib.get_option_dict(get_cuffquant_config_file())

    # get the options
    experiment_id = cuffquant_option_dict['identification']['experiment_id']
    reference_dataset_id = cuffquant_option_dict['identification']['reference_dataset_id']
    mask_file = cuffquant_option_dict['identification']['mask_file']
    assembly_software = cuffquant_option_dict['identification']['assembly_software']
    assembly_dataset_id = cuffquant_option_dict['identification']['assembly_dataset_id']
    threads = cuffquant_option_dict['Cuffquant parameters']['threads']
    library_type = cuffquant_option_dict['Cuffquant parameters']['library_type']
    frag_len_mean = cuffquant_option_dict['Cuffquant parameters']['frag_len_mean']
    frag_len_std_dev = cuffquant_option_dict['Cuffquant parameters']['frag_len_std_dev']
    max_mle_iterations = cuffquant_option_dict['Cuffquant parameters']['max_mle_iterations']
    max_bundle_frags = cuffquant_option_dict['Cuffquant parameters']['max_bundle_frags']
    other_parameters = cuffquant_option_dict['Cuffquant parameters']['other_parameters']

    # get the sections list
    sections_list = []
    for section in cuffquant_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # set the path of the file with the alignment dataset identification list
    alignment_dataset_id_list_file = '{0}/alignment_dataset_id_list.txt'.format(current_run_dir)

    # set the path of the file with the sample sheet
    sample_sheet_file = '{0}/sample_sheet.txt'.format(current_run_dir)

    # build alignment dataset identification list
    alignment_software_list = []
    alignment_dataset_id_list = []
    group_label_list = []
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^alignment-dataset-[0-9]+$', section):
            alignment_software_list.append(cuffquant_option_dict[section]['alignment_software'])
            alignment_dataset_id_list.append(cuffquant_option_dict[section]['alignment_dataset_id'])
            group_label_list.append(cuffquant_option_dict[section]['group_label'])

    # set the mask file path
    if mask_file.upper() != 'NONE':
        mask_file = xlib.get_cluster_reference_file(reference_dataset_id, mask_file)

    # set the transcriptome file path
    transcriptome_file = xlib.get_cluster_result_file(experiment_id, assembly_dataset_id, 'merged.gtf')

    # write the Cuffquant process script
    try:
        if not os.path.exists(os.path.dirname(get_cuffquant_process_script())):
            os.makedirs(os.path.dirname(get_cuffquant_process_script()))
        with open(get_cuffquant_process_script(), mode='w', encoding='iso-8859-1', newline='\n') as script_file_id:
            script_file_id.write( '#!/bin/bash\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'SEP="#########################################"\n')
            script_file_id.write( 'export HOST_IP=`curl --silent checkip.amazonaws.com`\n')
            script_file_id.write( 'export HOST_ADDRESS="ec2-${HOST_IP//./-}-compute-1.amazonaws.com"\n')
            script_file_id.write( '{0}\n'.format('CUFFLINKS_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_cufflinks_bioconda_code())))
            script_file_id.write( '{0}\n'.format('export PATH=$CUFFLINKS_PATH:$PATH'))
            script_file_id.write( '{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            script_file_id.write( '{0}\n'.format('source activate {0}'.format(xlib.get_cufflinks_bioconda_code())))
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('STATUS_DIR={0}'.format(xlib.get_status_dir(current_run_dir))))
            script_file_id.write( '{0}\n'.format('SCRIPT_STATUS_OK={0}'.format(xlib.get_status_ok(current_run_dir))))
            script_file_id.write( '{0}\n'.format('SCRIPT_STATUS_WRONG={0}'.format(xlib.get_status_wrong(current_run_dir))))
            script_file_id.write( '{0}\n'.format('mkdir --parents $STATUS_DIR'))
            script_file_id.write( '{0}\n'.format('if [ -f $SCRIPT_STATUS_OK ]; then rm $SCRIPT_STATUS_OK; fi'))
            script_file_id.write( '{0}\n'.format('if [ -f $SCRIPT_STATUS_WRONG ]; then rm $SCRIPT_STATUS_WRONG; fi'))
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function init\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    INIT_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "Script started at $FORMATTED_INIT_DATETIME+00:00."\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write(f'    echo "CLUSTER: {cluster_name}"\n')
            script_file_id.write(f'    echo "HOST_IP: $HOST_IP - HOST_ADDRESS: $HOST_ADDRESS"\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function create_alignment_dataset_list_file'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Creation of alignment dataset list file ..."'))
            script_file_id.write( '{0}\n'.format('    touch {0}'.format(alignment_dataset_id_list_file)))
            for i in range(len(alignment_dataset_id_list)):
                script_file_id.write( '{0}\n'.format('    echo "{0}" >> {1}'.format(alignment_dataset_id_list[i], alignment_dataset_id_list_file)))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function create_sample_sheet_file'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Creation of sample sheet file ..."'))
            script_file_id.write( '{0}\n'.format('    touch {0}'.format(sample_sheet_file)))
            script_file_id.write( '{0}\n'.format('    echo "sample_id\tgroup_label" >> {0}'.format(sample_sheet_file)))
            for i in range(len(alignment_dataset_id_list)):
                script_file_id.write( '{0}\n'.format('    echo "{0}/{1}/abundances.cxb\t{2}" >> {3}'.format(current_run_dir, alignment_dataset_id_list[i], group_label_list[i], sample_sheet_file)))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function run_cuffquant_process'))
            script_file_id.write( '{\n')
            for i in range(len(alignment_dataset_id_list)):
                script_file_id.write( '{0}\n'.format('    mkdir --parents {0}/{1}'.format(current_run_dir, alignment_dataset_id_list[i])))
                script_file_id.write( '{0}\n'.format('    cd {0}/{1}'.format(current_run_dir, alignment_dataset_id_list[i])))
                script_file_id.write( '    echo "$SEP"\n')
                if alignment_software_list[i] == xlib.get_star_code():
                    alignment_file = '{0}/starAligned.sortedByCoord.out.bam'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, alignment_dataset_id_list[i]))
                elif alignment_software_list[i] == xlib.get_tophat_code():
                    alignment_file = '{0}/accepted_hits.bam'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, alignment_dataset_id_list[i]))
                script_file_id.write( '{0}\n'.format('    echo "Cuffquant process  for alignment dataset {0}..."'.format(alignment_dataset_id_list[i])))
                script_file_id.write( '{0}\n'.format('    /usr/bin/time \\'))
                script_file_id.write( '{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
                script_file_id.write( '{0}\n'.format('        cuffquant \\'))
                script_file_id.write( '{0}\n'.format('            --no-update-check \\'))
                script_file_id.write( '{0}\n'.format('            --num-threads {0} \\'.format(threads)))
                if mask_file.upper() != 'NONE':
                    script_file_id.write( '{0}\n'.format('            --mask-file {0} \\'.format(mask_file)))
                script_file_id.write( '{0}\n'.format('            --library-type {0} \\'.format(library_type)))
                script_file_id.write( '{0}\n'.format('            --frag-len-mean {0} \\'.format(frag_len_mean)))
                script_file_id.write( '{0}\n'.format('            --frag-len-std-dev {0} \\'.format(frag_len_std_dev)))
                script_file_id.write( '{0}\n'.format('            --max-mle-iterations {0} \\'.format(max_mle_iterations)))
                script_file_id.write( '{0}\n'.format('            --max-bundle-frags {0} \\'.format(max_bundle_frags)))
                if other_parameters.upper() != 'NONE':
                    parameter_list = [x.strip() for x in other_parameters.split(';')]
                    for i in range(len(parameter_list)):
                        if parameter_list[i].find('=') > 0:
                            pattern = r'^--(.+)=(.+)$'
                            mo = re.search(pattern, parameter_list[i])
                            parameter_name = mo.group(1).strip()
                            parameter_value = mo.group(2).strip()
                            script_file_id.write( '{0}\n'.format('            --{0} {1} \\'.format(parameter_name, parameter_value)))
                        else:
                            pattern = r'^--(.+)$'
                            mo = re.search(pattern, parameter_list[i])
                            parameter_name = mo.group(1).strip()
                            script_file_id.write( '{0}\n'.format('            --{0} \\'.format(parameter_name)))
                script_file_id.write( '{0}\n'.format('            --output-dir {0}/{1} \\'.format(current_run_dir, alignment_dataset_id_list[i])))
                script_file_id.write( '{0}\n'.format('            {0} \\'.format(transcriptome_file)))
                script_file_id.write( '{0}\n'.format('            {0}'.format(alignment_file)))
                script_file_id.write( '{0}\n'.format('    RC=$?'))
                script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error cuffquant $RC; fi'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function end'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            script_file_id.write( '{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            script_file_id.write( '{0}\n'.format('    calculate_duration'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Script ended OK at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            script_file_id.write( '{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_cuffquant_name())))
            script_file_id.write( '{0}\n'.format('    MESSAGE="{0}"'.format(xlib.get_mail_message_ok(xlib.get_cuffquant_name(), cluster_name))))
            script_file_id.write( '    mail --append "Content-type: text/html;" --append "FROM:root@NGScloud2" --subject="$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"\n')
            script_file_id.write( '{0}\n'.format('    touch $SCRIPT_STATUS_OK'))
            script_file_id.write( '{0}\n'.format('    exit 0'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function manage_error'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            script_file_id.write( '{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            script_file_id.write( '{0}\n'.format('    calculate_duration'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "ERROR: $1 returned error $2"'))
            script_file_id.write( '{0}\n'.format('    echo "Script ended WRONG at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            script_file_id.write( '{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_cuffquant_name())))
            script_file_id.write( '{0}\n'.format('    MESSAGE="{0}"'.format(xlib.get_mail_message_wrong(xlib.get_cuffquant_name(), cluster_name))))
            script_file_id.write( '    mail --append "Content-type: text/html;" --append "FROM:root@NGScloud2" --subject="$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"\n')
            script_file_id.write( '{0}\n'.format('    touch $SCRIPT_STATUS_WRONG'))
            script_file_id.write( '{0}\n'.format('    exit 3'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function calculate_duration\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    DURATION=`expr $END_DATETIME - $INIT_DATETIME`\n')
            script_file_id.write( '    HH=`expr $DURATION / 3600`\n')
            script_file_id.write( '    MM=`expr $DURATION % 3600 / 60`\n')
            script_file_id.write( '    SS=`expr $DURATION % 60`\n')
            script_file_id.write( '    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'init\n')
            script_file_id.write( '{0}\n'.format('create_alignment_dataset_list_file'))
            script_file_id.write( '{0}\n'.format('create_sample_sheet_file'))
            script_file_id.write( '{0}\n'.format('run_cuffquant_process'))
            script_file_id.write( 'end\n')
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_cuffquant_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_cuffquant_process_starter(current_run_dir):
    '''
    Build the starter of the current Cuffquant process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Cuffquant process starter
    try:
        if not os.path.exists(os.path.dirname(get_cuffquant_process_starter())):
            os.makedirs(os.path.dirname(get_cuffquant_process_starter()))
        with open(get_cuffquant_process_starter(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '{0}\n'.format('#!/bin/bash'))
            file_id.write( '{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write( '{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_cuffquant_process_script()), xlib.get_cluster_log_file())))
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_cuffquant_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_cuffquant_config_file():
    '''
    Get the Cuffquant config file path.
    '''

    # assign the Cuffquant config file path
    cuffquant_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_cuffquant_code())

    # return the Cuffquant config file path
    return cuffquant_config_file

#-------------------------------------------------------------------------------

def get_cuffquant_process_script():
    '''
    Get the Cuffquant process script path in the local computer.
    '''

    # assign the Cuffquant script path
    cuffquant_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_cuffquant_code())

    # return the Cuffquant script path
    return cuffquant_process_script

#-------------------------------------------------------------------------------

def get_cuffquant_process_starter():
    '''
    Get the Cuffquant process starter path in the local computer.
    '''

    # assign the Cuffquant process starter path
    cuffquant_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_cuffquant_code())

    # return the Cuffquant starter path
    return cuffquant_process_starter

#-------------------------------------------------------------------------------

def create_cuffdiff_config_file(experiment_id='exp001', assembly_dataset_id='cufflnkmrg-170101-235959', quantitation_dataset_id='cuffquant-170101-235959'):
    '''
    Create Cuffdiff config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # set the assembly software
    if assembly_dataset_id.startswith(xlib.get_cufflinks_cuffmerge_code()):
        assembly_software = xlib.get_cufflinks_cuffmerge_code()

    # set the quantitation software
    if quantitation_dataset_id.startswith(xlib.get_cuffquant_code()):
        quantitation_software = xlib.get_cuffquant_code()

    # create the Cuffdiff config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_cuffdiff_config_file())):
            os.makedirs(os.path.dirname(get_cuffdiff_config_file()))
        with open(get_cuffdiff_config_file(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# The reference and GTF files have to be located in the cluster directory {0}/experiment_id/reference_dataset_id'.format(xlib.get_cluster_reference_dir())))
            file_id.write( '{0}\n'.format('# The experiment_id, alignment_dataset_id and assembly_dataset_id names are fixed in the identification section.'))
            file_id.write( '{0}\n'.format('# The assembly files have to be located in the cluster directory {0}/experiment_id/assembly_dataset_id'.format(xlib.get_cluster_result_dir())))
            file_id.write( '{0}\n'.format('# The quantitation files have to be located in the cluster directory {0}/experiment_id/quantitation_dataset_id'.format(xlib.get_cluster_result_dir())))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# You can consult the parameters of Cuffdiff and their meaning in http://cole-trapnell-lab.github.io/cufflinks/.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# In section "Cuffdiff parameters", the key "other_parameters" allows you to input additional parameters in the format:'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('#    other_parameters = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('# parameter-i is a parameter name of Cuffdiff and value-i a valid value of parameter-i, e.g.'))
            file_id.write( '{0}\n'.format('#'))
            file_id.write( '{0}\n'.format('#    other_parameters = --multi-read-correct; --no-length-correction'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information identifies the experiment.'))
            file_id.write( '{0}\n'.format('[identification]'))
            file_id.write( '{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write( '{0:<50} {1}\n'.format('assembly_software = {0}'.format(assembly_software), '# assembly software: {0})'.format(get_assembly_software_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('assembly_dataset_id = {0}'.format(assembly_dataset_id), '# assembly dataset identification'))
            file_id.write( '{0:<50} {1}\n'.format('quantitation_software = {0}'.format(quantitation_software), '#quantitation software: {0}'.format(get_quantitation_software_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('quantitation_dataset_id = {0}'.format(quantitation_dataset_id), '# quantitation dataset identification'))
            file_id.write( '\n')
            file_id.write( '{0}\n'.format('# This section has the information to set the Cuffdiff parameters'))
            file_id.write( '{0}\n'.format('[Cuffdiff parameters]'))
            file_id.write( '{0:<50} {1}\n'.format('threads = 4', '# number of threads for use'))
            file_id.write( '{0:<50} {1}\n'.format('library_type = FR-UNSTRANDED', '# library type: {0}'.format(get_library_type_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('total_hits_norm = NO', '# count all fragments, including those not compatible with any reference transcript, towards the number of mapped fragments used in the FPKM denominator: {0}'.format(get_total_hits_norm_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('compatible_hits_norm = YES', '# count only those fragments compatible with some reference transcript towards the number of mapped fragments used in the FPKM denominator: {0}'.format(get_compatible_hits_norm_code_list_text())))
            file_id.write( '{0:<50} {1}\n'.format('min_alignment_count = 10', '# minimum number of alignments in a locus for needed to conduct significance testing on changes in that locus observed between samples'))
            file_id.write( '{0:<50} {1}\n'.format('fdr = 0.05', '# allowed false discovery rate'))
            file_id.write( '{0:<50} {1}\n'.format('frag_len_mean = 200', '# expected (mean) fragment length'))
            file_id.write( '{0:<50} {1}\n'.format('frag_len_std_dev = 80', '# standard deviation for the distribution on fragment lengths'))
            file_id.write( '{0:<50} {1}\n'.format('max_mle_iterations = 5000', '# number of iterations allowed during maximum likelihood estimation of abundances'))
            file_id.write( '{0:<50} {1}\n'.format('max_bundle_frags = 1000000', '# maximum number of fragments a locus may have before being skipped'))
            file_id.write( '{0:<50} {1}\n'.format('other_parameters = NONE', '# additional parameters to the previous ones or NONE'))
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_cufflinks_cuffmerge_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_cuffdiff_process(cluster_name, log, function=None):
    '''
    Run a Cuffdiff process.
    '''

    # initialize the control variable
    OK = True

    # get the Cuffdiff option dictionary
    cuffdiff_option_dict = xlib.get_option_dict(get_cuffdiff_config_file())

    # get the experiment identification
    experiment_id = cuffdiff_option_dict['identification']['experiment_id']

    # warn that the log window does not have to be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # check the Cuffdiff config file
    log.write(f'{xlib.get_separator()}\n')
    log.write('Checking the {0} config file ...\n'.format(xlib.get_cuffdiff_name()))
    (OK, error_list) = check_cuffdiff_config_file(strict=True)
    if OK:
        log.write('The file is OK.\n')
    else:
        log.write('*** ERROR: The config file is not valid.\n')
        log.write('Please correct this file or recreate the config files.\n')

    # create the SSH client connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SSH client ...\n')
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name)
        if OK:
            log.write('The SSH client is connected.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # create the SSH transport connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SSH transport ...\n')
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name)
        if OK:
            log.write('The SSH transport is connected.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # create the SFTP client 
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Connecting the SFTP client ...\n')
        sftp_client = xssh.create_sftp_client(ssh_transport)
        log.write('The SFTP client is connected.\n')

    # warn that the requirements are being verified 
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Checking process requirements ...\n')

    # check the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name)
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # check Cufflinks is installed
    if OK:
        (OK, error_list, is_installed) = xbioinfoapp.is_installed_bioconda_package(xlib.get_cufflinks_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_installed:
                log.write('*** ERROR: {0} is not installed.\n'.format(xlib.get_cufflinks_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} installation could not be performed.\n'.format(xlib.get_cufflinks_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_cuffdiff_code())
        command = f'mkdir --parents {current_run_dir}'
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Cuffdiff process script
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process script {0} ...\n'.format(get_cuffdiff_process_script()))
        (OK, error_list) = build_cuffdiff_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Cuffdiff process script to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(get_cuffdiff_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_cuffdiff_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_cuffdiff_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Cuffdiff process script in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_cuffdiff_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_cuffdiff_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # build the Cuffdiff process starter
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Building the process starter {0} ...\n'.format(get_cuffdiff_process_starter()))
        (OK, error_list) = build_cuffdiff_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Cuffdiff process starter to the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(get_cuffdiff_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_cuffdiff_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_cuffdiff_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write(f'{error}\n')

    # set run permision to the Cuffdiff process starter in the cluster
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_cuffdiff_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_cuffdiff_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write(f'*** ERROR: Wrong command ---> {command}\n')

    # submit the Cuffdiff process
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_cuffdiff_process_starter())))
        OK = xssh.submit_script(cluster_name, ssh_client, current_run_dir, os.path.basename(get_cuffdiff_process_starter()), log)

    # close the SSH transport connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Closing the SSH transport connection ...\n')
        xssh.close_ssh_transport_connection(ssh_transport)
        log.write('The connection is closed.\n')

    # close the SSH client connection
    if OK:
        log.write(f'{xlib.get_separator()}\n')
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write(f'{xlib.get_separator()}\n')
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def check_cuffdiff_config_file(strict):
    '''
    Check the Cuffdiff config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        cuffdiff_option_dict = xlib.get_option_dict(get_cuffdiff_config_file())
    except Exception as e:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in cuffdiff_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = cuffdiff_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "assembly_software"
            assembly_software = cuffdiff_option_dict.get('identification', {}).get('assembly_software', not_found)
            if assembly_software == not_found:
                error_list.append('*** ERROR: the key "assembly_software" is not found in the section "identification".')
                OK = False
            elif not xlib.check_code(assembly_software, get_assembly_software_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "assembly_software" has to be {0}.'.format(get_assembly_software_code_list_text()))
                OK = False

            # check section "identification" - key "assembly_dataset_id"
            assembly_dataset_id = cuffdiff_option_dict.get('identification', {}).get('assembly_dataset_id', not_found)
            if assembly_dataset_id == not_found:
                error_list.append('*** ERROR: the key "assembly_dataset_id" is not found in the section "identification".')
                OK = False
            elif not xlib.check_startswith(assembly_dataset_id, get_assembly_software_code_list(), case_sensitive=True):
                error_list.append('*** ERROR: the key "assembly_dataset_id" has to start with {0}.'.format(get_assembly_software_code_list_text()))
                OK = False

            # check section "identification" - key "quantitation_software"
            quantitation_software = cuffdiff_option_dict.get('identification', {}).get('quantitation_software', not_found)
            if quantitation_software == not_found:
                error_list.append('*** ERROR: the key "quantitation_software" is not found in the section "identification".')
                OK = False
            elif not xlib.check_code(quantitation_software, get_quantitation_software_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "quantitation_software" has to be {0}.'.format(get_quantitation_software_code_list_text()))
                OK = False

            # check section "identification" - key "quantitation_dataset_id"
            quantitation_dataset_id = cuffdiff_option_dict.get('identification', {}).get('quantitation_dataset_id', not_found)
            if quantitation_dataset_id == not_found:
                error_list.append('*** ERROR: the key "quantitation_dataset_id" is not found in the section "identification".')
                OK = False
            elif not xlib.check_startswith(quantitation_dataset_id, get_quantitation_software_code_list(), case_sensitive=True):
                error_list.append('*** ERROR: the key "quantitation_dataset_id" has to start with {0}.'.format(get_quantitation_software_code_list_text()))
                OK = False

        # check section "Cuffdiff parameters"
        if 'Cuffdiff parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Cuffdiff parameters" is not found.')
            OK = False
        else:

            # check section "Cuffdiff parameters" - key "threads"
            threads = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('threads', not_found)
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_int(threads, minimum=1):
                error_list.append('*** ERROR: the key "threads" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffdiff parameters" - key "library_type"
            library_type = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('library_type', not_found).lower()
            if library_type == not_found:
                error_list.append('*** ERROR: the key "library_type" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_code(library_type, get_library_type_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "library_type" has to be {0}.'.format(get_library_type_code_list_text()))
                OK = False

            # check section "Cuffdiff parameters" - key "total_hits_norm"
            total_hits_norm = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('total_hits_norm', not_found)
            if total_hits_norm == not_found:
                error_list.append('*** ERROR: the key "total_hits_norm" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_code(total_hits_norm, get_total_hits_norm_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "total_hits_norm" has to be {0}.'.format(get_total_hits_norm_code_list_text()))

            # check section "Cuffdiff parameters" - key "compatible_hits_norm"
            compatible_hits_norm = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('compatible_hits_norm', not_found)
            if compatible_hits_norm == not_found:
                error_list.append('*** ERROR: the key "compatible_hits_norm" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_code(compatible_hits_norm, get_compatible_hits_norm_code_list(), case_sensitive=False):
                error_list.append('*** ERROR: the key "compatible_hits_norm" has to be {0}.'.format(get_compatible_hits_norm_code_list_text()))

            # check section "Cuffdiff parameters" - key "min_alignment_count"
            min_alignment_count = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('min_alignment_count', not_found)
            if min_alignment_count == not_found:
                error_list.append('*** ERROR: the key "min_alignment_count" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_int(min_alignment_count, minimum=1):
                error_list.append('*** ERROR: the key "min_alignment_count" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffdiff parameters" - key "FDR"
            fdr = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('fdr', not_found)
            if fdr == not_found:
                error_list.append('*** ERROR: the key "FDR" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_float(fdr, minimum=0., maximum=1.):
                error_list.append('*** ERROR: the key "FDR" has to be a float number between 0.0 and 1.0.')
                OK = False

            # check section "Cuffdiff parameters" - key "frag_len_mean"
            frag_len_mean = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('frag_len_mean', not_found)
            if frag_len_mean == not_found:
                error_list.append('*** ERROR: the key "frag_len_mean" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_int(frag_len_mean, minimum=1):
                error_list.append('*** ERROR: the key "frag_len_mean" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffdiff parameters" - key "frag_len_std_dev"
            frag_len_std_dev = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('frag_len_std_dev', not_found)
            if frag_len_std_dev == not_found:
                error_list.append('*** ERROR: the key "frag_len_std_dev" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_int(frag_len_std_dev, minimum=1):
                error_list.append('*** ERROR: the key "frag_len_std_dev" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffdiff parameters" - key "max_mle_iterations"
            max_mle_iterations = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('max_mle_iterations', not_found)
            if max_mle_iterations == not_found:
                error_list.append('*** ERROR: the key "max_mle_iterations" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_int(max_mle_iterations, minimum=1):
                error_list.append('*** ERROR: the key "max_mle_iterations" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffdiff parameters" - key "max_bundle_frags"
            max_bundle_frags = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('max_bundle_frags', not_found)
            if max_bundle_frags == not_found:
                error_list.append('*** ERROR: the key "max_bundle_frags" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif not xlib.check_int(max_bundle_frags, minimum=1):
                error_list.append('*** ERROR: the key "max_bundle_frags" has to be an integer number greater than or equal to 1.')
                OK = False

            # check section "Cuffdiff parameters" - key "other_parameters"
            not_allowed_parameters_list = ['no-update-check', 'num-threads', 'mask-file', 'library_type', 'total-hits-norm', 'compatible-hits-norm', 'min-alignment-count', 'FDR', 'output-dir', 'frag-len-mean', 'frag-len-std-dev', 'max-mle-iterations', 'max-bundle-frags']
            other_parameters = cuffdiff_option_dict.get('Cuffdiff parameters', {}).get('other_parameters', not_found)
            if other_parameters == not_found:
                error_list.append('*** ERROR: the key "other_parameters" is not found in the section "Cuffdiff parameters".')
                OK = False
            elif other_parameters.upper() != 'NONE':
                (OK, error_list2) = xlib.check_parameter_list(other_parameters, "other_parameters", not_allowed_parameters_list)
                error_list = error_list + error_list2

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_cuffdiff_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_cuffdiff_process_script(cluster_name, current_run_dir):
    '''
    Build the current Cuffdiff process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the Cuffdiff option dictionary
    cuffdiff_option_dict = xlib.get_option_dict(get_cuffdiff_config_file())

    # get the options
    experiment_id = cuffdiff_option_dict['identification']['experiment_id']
    assembly_software = cuffdiff_option_dict['identification']['assembly_software']
    assembly_dataset_id = cuffdiff_option_dict['identification']['assembly_dataset_id']
    quantitation_software = cuffdiff_option_dict['identification']['quantitation_software']
    quantitation_dataset_id = cuffdiff_option_dict['identification']['quantitation_dataset_id']
    threads = cuffdiff_option_dict['Cuffdiff parameters']['threads']
    library_type = cuffdiff_option_dict['Cuffdiff parameters']['library_type']
    total_hits_norm = cuffdiff_option_dict['Cuffdiff parameters']['total_hits_norm']
    compatible_hits_norm = cuffdiff_option_dict['Cuffdiff parameters']['compatible_hits_norm']
    min_alignment_count = cuffdiff_option_dict['Cuffdiff parameters']['min_alignment_count']
    fdr = cuffdiff_option_dict['Cuffdiff parameters']['fdr']
    frag_len_mean = cuffdiff_option_dict['Cuffdiff parameters']['frag_len_mean']
    frag_len_std_dev = cuffdiff_option_dict['Cuffdiff parameters']['frag_len_std_dev']
    max_mle_iterations = cuffdiff_option_dict['Cuffdiff parameters']['max_mle_iterations']
    max_bundle_frags = cuffdiff_option_dict['Cuffdiff parameters']['max_bundle_frags']
    other_parameters = cuffdiff_option_dict['Cuffdiff parameters']['other_parameters']

    # set the file path of the alignment dataset identification list in the quantitation dataset
    quantitation_alignment_dataset_id_list_file = xlib.get_cluster_result_file(experiment_id, quantitation_dataset_id, 'alignment_dataset_id_list.txt')

    # set the file path of the alignment dataset identification list in the current directory
    current_alignment_dataset_id_list_file = '{0}/alignment_dataset_id_list.txt'.format(current_run_dir)

    # set the path of the file with the sample sheet in the quantitation dataset
    quantitation_sample_sheet_file = xlib.get_cluster_result_file(experiment_id, quantitation_dataset_id, 'sample_sheet.txt')

    # set the path of the file with the sample sheet in the current directory
    current_sample_sheet_file = '{0}/sample_sheet.txt'.format(current_run_dir)

    # set the transcriptome file path
    transcriptome_file = xlib.get_cluster_result_file(experiment_id, assembly_dataset_id, 'merged.gtf')

    # set the quantitation dataset path
    quantitation_dataset_path = xlib.get_cluster_experiment_result_dataset_dir(experiment_id, quantitation_dataset_id)

    # write the Cuffdiff process script
    try:
        if not os.path.exists(os.path.dirname(get_cuffdiff_process_script())):
            os.makedirs(os.path.dirname(get_cuffdiff_process_script()))
        with open(get_cuffdiff_process_script(), mode='w', encoding='iso-8859-1', newline='\n') as script_file_id:
            script_file_id.write( '#!/bin/bash\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'SEP="#########################################"\n')
            script_file_id.write( 'export HOST_IP=`curl --silent checkip.amazonaws.com`\n')
            script_file_id.write( 'export HOST_ADDRESS="ec2-${HOST_IP//./-}-compute-1.amazonaws.com"\n')
            script_file_id.write( '{0}\n'.format('CUFFLINKS_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_cufflinks_bioconda_code())))
            script_file_id.write( '{0}\n'.format('export PATH=$CUFFLINKS_PATH:$PATH'))
            script_file_id.write( '{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            script_file_id.write( '{0}\n'.format('source activate {0}'.format(xlib.get_cufflinks_bioconda_code())))
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('STATUS_DIR={0}'.format(xlib.get_status_dir(current_run_dir))))
            script_file_id.write( '{0}\n'.format('SCRIPT_STATUS_OK={0}'.format(xlib.get_status_ok(current_run_dir))))
            script_file_id.write( '{0}\n'.format('SCRIPT_STATUS_WRONG={0}'.format(xlib.get_status_wrong(current_run_dir))))
            script_file_id.write( '{0}\n'.format('mkdir --parents $STATUS_DIR'))
            script_file_id.write( '{0}\n'.format('if [ -f $SCRIPT_STATUS_OK ]; then rm $SCRIPT_STATUS_OK; fi'))
            script_file_id.write( '{0}\n'.format('if [ -f $SCRIPT_STATUS_WRONG ]; then rm $SCRIPT_STATUS_WRONG; fi'))
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function init\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    INIT_DATETIME=`date --utc +%s`\n')
            script_file_id.write( '    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '    echo "Script started at $FORMATTED_INIT_DATETIME+00:00."\n')
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write(f'    echo "CLUSTER: {cluster_name}"\n')
            script_file_id.write(f'    echo "HOST_IP: $HOST_IP - HOST_ADDRESS: $HOST_ADDRESS"\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function copy_alignment_dataset_list_file'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Copying the alignment dataset list file ..."'))
            script_file_id.write( '{0}\n'.format('    cp {0} {1}'.format(quantitation_alignment_dataset_id_list_file, current_alignment_dataset_id_list_file)))
            script_file_id.write( '{0}\n'.format('    RC=$?'))
            script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error cp $RC; fi'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function copy_sample_sheet_file'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Copying the sample sheet file ..."'))
            script_file_id.write( '{0}\n'.format('    cp {0} {1}'.format(quantitation_sample_sheet_file, current_sample_sheet_file)))
            script_file_id.write( '{0}\n'.format('    RC=$?'))
            script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error cp $RC; fi'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function create_cuffquant_output_abundance_list_file'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Create Cufflinks output gtf list file ..."'))
            script_file_id.write( '{0}\n'.format('    ABUNDANCE_FILE_LIST=""'))
            script_file_id.write( '{0}\n'.format('    while read LINE; do'))
            script_file_id.write( '{0}\n'.format('        ABUNDANCE_FILE={0}/$LINE/abundances.cxb'.format(quantitation_dataset_path)))
            script_file_id.write( '{0}\n'.format('        if [ "$ABUNDANCE_FILE_LIST" == "" ]; then'))
            script_file_id.write( '{0}\n'.format('            ABUNDANCE_FILE_LIST=$ABUNDANCE_FILE'))
            script_file_id.write( '{0}\n'.format('        else'))
            script_file_id.write( '{0}\n'.format('            ABUNDANCE_FILE_LIST=$ABUNDANCE_FILE_LIST" "$ABUNDANCE_FILE'))
            script_file_id.write( '{0}\n'.format('        fi'))
            script_file_id.write( '{0}\n'.format('    done < {0}'.format(current_alignment_dataset_id_list_file)))
            script_file_id.write( '{0}\n'.format('    echo "ABUNDANCE_FILE_LIST: $ABUNDANCE_FILE_LIST"'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function run_cuffdiff_process'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    cd {0}'.format(current_run_dir)))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Cuffdiff process ..."'))
            script_file_id.write( '{0}\n'.format('    /usr/bin/time \\'))
            script_file_id.write( '{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            script_file_id.write( '{0}\n'.format('        cuffdiff \\'))
            script_file_id.write( '{0}\n'.format('            --no-update-check \\'))
            script_file_id.write( '{0}\n'.format('            --num-threads {0} \\'.format(threads)))
            script_file_id.write( '{0}\n'.format('            --library-type {0} \\'.format(library_type)))
            if total_hits_norm.upper() == 'YES':
                script_file_id.write( '{0}\n'.format('            --total-hits-norm \\'))
            if compatible_hits_norm.upper() == 'YES':
                script_file_id.write( '{0}\n'.format('            --compatible-hits-norm \\'))
            script_file_id.write( '{0}\n'.format('            --min-alignment-count {0} \\'.format(min_alignment_count)))
            script_file_id.write( '{0}\n'.format('            --FDR {0} \\'.format(fdr)))
            script_file_id.write( '{0}\n'.format('            --frag-len-mean {0} \\'.format(frag_len_mean)))
            script_file_id.write( '{0}\n'.format('            --frag-len-std-dev {0} \\'.format(frag_len_std_dev)))
            script_file_id.write( '{0}\n'.format('            --max-mle-iterations {0} \\'.format(max_mle_iterations)))
            script_file_id.write( '{0}\n'.format('            --max-bundle-frags {0} \\'.format(max_bundle_frags)))
            if other_parameters.upper() != 'NONE':
                parameter_list = [x.strip() for x in other_parameters.split(';')]
                for i in range(len(parameter_list)):
                    if parameter_list[i].find('=') > 0:
                        pattern = r'^--(.+)=(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        parameter_value = mo.group(2).strip()
                        script_file_id.write( '{0}\n'.format('            --{0} {1} \\'.format(parameter_name, parameter_value)))
                    else:
                        pattern = r'^--(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        script_file_id.write( '{0}\n'.format('            --{0} \\'.format(parameter_name)))
            script_file_id.write( '{0}\n'.format('            --output-dir {0} \\'.format(current_run_dir)))
            script_file_id.write( '{0}\n'.format('            --use-sample-sheet \\'))
            script_file_id.write( '{0}\n'.format('            {0} \\'.format(transcriptome_file)))
            #--file_id.write( '{0}\n'.format('            $ABUNDANCE_FILE_LIST'))
            script_file_id.write( '{0}\n'.format('            {0} \\'.format(current_sample_sheet_file)))
            script_file_id.write( '{0}\n'.format('    RC=$?'))
            script_file_id.write( '{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error cuffdiff $RC; fi'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function end'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            script_file_id.write( '{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            script_file_id.write( '{0}\n'.format('    calculate_duration'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "Script ended OK at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            script_file_id.write( '{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_cuffdiff_name())))
            script_file_id.write( '{0}\n'.format('    MESSAGE="{0}"'.format(xlib.get_mail_message_ok(xlib.get_cuffdiff_name(), cluster_name))))
            script_file_id.write( '    mail --append "Content-type: text/html;" --append "FROM:root@NGScloud2" --subject="$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"\n')
            script_file_id.write( '{0}\n'.format('    touch $SCRIPT_STATUS_OK'))
            script_file_id.write( '{0}\n'.format('    exit 0'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( '{0}\n'.format('function manage_error'))
            script_file_id.write( '{\n')
            script_file_id.write( '{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            script_file_id.write( '{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            script_file_id.write( '{0}\n'.format('    calculate_duration'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    echo "ERROR: $1 returned error $2"'))
            script_file_id.write( '{0}\n'.format('    echo "Script ended WRONG at $FORMATTED_END_DATETIME+00:00 with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            script_file_id.write( '    echo "$SEP"\n')
            script_file_id.write( '{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            script_file_id.write( '{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_cuffdiff_name())))
            script_file_id.write( '{0}\n'.format('    MESSAGE="{0}"'.format(xlib.get_mail_message_wrong(xlib.get_cuffdiff_name(), cluster_name))))
            script_file_id.write( '    mail --append "Content-type: text/html;" --append "FROM:root@NGScloud2" --subject="$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"\n')
            script_file_id.write( '{0}\n'.format('    touch $SCRIPT_STATUS_WRONG'))
            script_file_id.write( '{0}\n'.format('    exit 3'))
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'function calculate_duration\n')
            script_file_id.write( '{\n')
            script_file_id.write( '    DURATION=`expr $END_DATETIME - $INIT_DATETIME`\n')
            script_file_id.write( '    HH=`expr $DURATION / 3600`\n')
            script_file_id.write( '    MM=`expr $DURATION % 3600 / 60`\n')
            script_file_id.write( '    SS=`expr $DURATION % 60`\n')
            script_file_id.write( '    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`\n')
            script_file_id.write( '}\n')
            script_file_id.write( '#-------------------------------------------------------------------------------\n')
            script_file_id.write( 'init\n')
            script_file_id.write( '{0}\n'.format('copy_alignment_dataset_list_file'))
            script_file_id.write( '{0}\n'.format('copy_sample_sheet_file'))
            script_file_id.write( '{0}\n'.format('run_cuffdiff_process'))
            script_file_id.write( 'end\n')
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_cuffdiff_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_cuffdiff_process_starter(current_run_dir):
    '''
    Build the starter of the current Cuffdiff process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Cuffdiff process starter
    try:
        if not os.path.exists(os.path.dirname(get_cuffdiff_process_starter())):
            os.makedirs(os.path.dirname(get_cuffdiff_process_starter()))
        with open(get_cuffdiff_process_starter(), mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '{0}\n'.format('#!/bin/bash'))
            file_id.write( '{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write( '{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_cuffdiff_process_script()), xlib.get_cluster_log_file())))
    except Exception as e:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_cuffdiff_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_cuffdiff_config_file():
    '''
    Get the Cuffdiff config file path.
    '''

    # assign the Cuffdiff config file path
    cuffdiff_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_cuffdiff_code())

    # return the Cuffdiff config file path
    return cuffdiff_config_file

#-------------------------------------------------------------------------------

def get_cuffdiff_process_script():
    '''
    Get the Cuffdiff process script path in the local computer.
    '''

    # assign the Cuffdiff script path
    cuffdiff_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_cuffdiff_code())

    # return the Cuffdiff script path
    return cuffdiff_process_script

#-------------------------------------------------------------------------------

def get_cuffdiff_process_starter():
    '''
    Get the Cuffdiff process starter path in the local computer.
    '''

    # assign the Cuffdiff process starter path
    cuffdiff_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_cuffdiff_code())

    # return the Cuffdiff starter path
    return cuffdiff_process_starter

#-------------------------------------------------------------------------------
    
def get_alignment_software_code_list():
    '''
    Get the code list of "alignment_software".
    '''

    return [xlib.get_star_code(), xlib.get_tophat_code()]

#-------------------------------------------------------------------------------
    
def get_alignment_software_code_list_text():
    '''
    Get the code list of "alignment_software" as text.
    '''

    return '{0} ({1}) or {2} ({3})'.format(xlib.get_star_code(), xlib.get_star_name(), xlib.get_tophat_code(), xlib.get_tophat_name())

#-------------------------------------------------------------------------------
    
def get_assembly_software_code_list():
    '''
    Get the code list of "assembly_software".
    '''

    return [xlib.get_cufflinks_cuffmerge_code()]

#-------------------------------------------------------------------------------
    
def get_assembly_software_code_list_text():
    '''
    Get the code list of "assembly_software" as text.
    '''

    return '{0} ({1})'.format(xlib.get_cufflinks_cuffmerge_code(), xlib.get_cufflinks_cuffmerge_name())

#-------------------------------------------------------------------------------
    
def get_quantitation_software_code_list():
    '''
    Get the code list of "quantitation_software".
    '''

    return [xlib.get_cuffquant_code()]

#-------------------------------------------------------------------------------
    
def get_quantitation_software_code_list_text():
    '''
    Get the code list of "quantitation_software" as text.
    '''

    return '{0} ({1})'.format(xlib.get_cuffquant_code(), xlib.get_cufflinks_cuffmerge_name())

#-------------------------------------------------------------------------------
    
def get_library_type_code_list():
    '''
    Get the code list of "library_type".
    '''

    return ['FR-FIRSTSTRAND', 'FR-SECONDSTRAND', 'FR-UNSTRANDED', 'FF-FIRSTSTRAND', 'FF-SECONDSTRAND', 'FF-UNSTRANDED', 'TRANSFRAGS']

#-------------------------------------------------------------------------------
    
def get_library_type_code_list_text():
    '''
    Get the code list of "library_type".
    '''

    return str(get_library_type_code_list()).strip('[]').replace('\'','').replace(',', ' or')

#-------------------------------------------------------------------------------
    
def get_total_hits_norm_code_list():
    '''
    Get the code list of "total_hits_norm".
    '''

    return ['YES', 'NO']

#-------------------------------------------------------------------------------
    
def get_total_hits_norm_code_list_text():
    '''
    Get the code list of "total_hits_norm" as text.
    '''

    return str(get_total_hits_norm_code_list()).strip('[]').replace('\'','').replace(',', ' or')

#-------------------------------------------------------------------------------
    
def get_compatible_hits_norm_code_list():
    '''
    Get the code list of "compatible_hits_norm".
    '''

    return ['YES', 'NO']

#-------------------------------------------------------------------------------
    
def get_compatible_hits_norm_code_list_text():
    '''
    Get the code list of "compatible_hits_norm" as text.
    '''

    return str(get_compatible_hits_norm_code_list()).strip('[]').replace('\'','').replace(',', ' or')

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the Cufflinks process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
