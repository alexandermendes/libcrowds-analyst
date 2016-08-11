# -*- coding: utf8 -*-
"""Analyst module for libcrowds-analyst."""

import sys
import enki
import time
import numpy as np


def _concat(df, col):
    """Return concatenated, non-duplicated column values.

    :param df: The dataframe of task runs (i.e enki.task_runs_df[task_id]).
    :param col: The name of the column.
    """
    deduped_df = df[col].drop_duplicates(keep='first')
    return '; '.join([item for item in deduped_df if len(item) > 0])


def _normalise_shelfmarks(df, col):
    """Normalise all shelfmarks in a dataframe.

    :param df: The dataframe.
    :param col: The name of the column.
    """
    df[col].replace(r',', '.', inplace=True)
    df[col].replace(r'\s+', '.', inplace=True)
    df[col].replace(r'\.+', '.', inplace=True)
    df[col].replace(r'\.$', '', inplace=True)
    df[col].replace(r'^\.', '.', inplace=True)
    df[col].replace(r'(?i)^chi', 'CHI', inplace=True)


def get_analyst_func(category_id):
    """Return the analyst function for a category."""
    func = 'category_{0}'.format(category_id)
    this_module = sys.modules[__name__]
    if hasattr(this_module, func):
        return getattr(this_module, func)


def category_1(api_key, endpoint, project_short_name, task_id, sleep=0):
    """Analyser for Convert-a-Card projects.

    The fields being compared are 'oclc' and 'shelfmark'. For all tasks where
    two or more contributors submitted the same answer the result will be set
    to that answer. For those tasks where no contributors were able to find a
    matching WorldCat record the result will be set to a blank value for both
    'oclc' and 'shelfmark'. All other tasks will remain unanalysed. The
    'comments' are added for all analysed results.
    """
    time.sleep(sleep)  # To throttle when many API calls
    e = enki.Enki(api_key, endpoint, project_short_name)
    e.get_tasks(task_id=task_id)
    e.get_task_runs()
    for t in e.tasks:
        r = enki.pbclient.find_results(e.project.id, task_id=task_id, all=1)[0]
        df = e.task_runs_df[t.id][['oclc', 'shelfmark']]
        comments = _concat(e.task_runs_df[t.id], 'comments')
        _normalise_shelfmarks(df, 'shelfmark')

        # Check for populated rows
        df = df.replace('', np.nan)
        if df.dropna(how='all').empty:
            r.info = dict(oclc="", shelfmark="", comments=comments)
            enki.pbclient.update_result(r)
            continue

        # Check for two or more matches
        df = df[df.duplicated(['oclc', 'shelfmark'], keep=False)]
        if not df.dropna(how='all').empty:
            r.info = dict(oclc=df.iloc[0]['oclc'],
                          shelfmark=df.iloc[0]['shelfmark'], comments=comments)
            enki.pbclient.update_result(r)
            continue

        # Unanalysed result
        r.info = 'Unanalysed'
        enki.pbclient.update_result(r)

    return "OK"
