import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
from textwrap import wrap

SHOW_PLOTS = True # Show interactive plot
SAVE_FIGS = False # Save jpg of plot
VOTETYPE_PLOTS = True # Show votetype plots (election day, mail, absentee, etc)
EXTRA_PLOTS = False # Non-presidential plots (400+ plots!)
FIRST_DIGIT_TEST = True # First digit or second digit Benford's law test

# Benford's law 1st digit test
if FIRST_DIGIT_TEST:
    S_BENFORDS = pd.Series(
        [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046],
        index=range(1,10)
    )
# 2nd digit test
else:
    S_BENFORDS = pd.Series(
        [0.12, 0.114, 0.109, 0.104, 0.1, 0.097, 0.093, 0.09, 0.088, 0.085],
        index=range(0,10)
    )

def totals_to_percentages(leading_nums, length):
    totals = 0
    if length == 1:
        totals = sum(leading_nums)
        if totals == 0:
            return None, None
        s_leading_nums = pd.Series(
            map(lambda x: x / totals, leading_nums),
            index=range(1,10) if FIRST_DIGIT_TEST else range(0, 10)
        )
    else:
        s_leading_nums = [None for _ in range(length)]
        # Convert nums to percentages
        for i in range(length):
            tot_nums = sum(leading_nums[i])
            totals += tot_nums
            s_leading_nums[i] = pd.Series(
                map(lambda x: x / tot_nums, leading_nums[i]),
                index=range(1,10) if FIRST_DIGIT_TEST else range(0, 10)
            )

    return totals, s_leading_nums

def set_bl_labels(p):
    p.set_xlabel('{} Digit Value'.format('Leading' if FIRST_DIGIT_TEST else 'Second'))
    p.set_ylabel('Proportion')
    p.legend(['Benford\'s law', 'Actual value'])

def plot_benfords_law(leading_nums, contest, choice, total_count, note, dir, biden_v_trump=False, all_3=False):
    totals = 0
    if not biden_v_trump and not all_3:
        # Convert nums to percentages
        totals, s_leading_nums = totals_to_percentages(leading_nums, 1)
        if totals == 0:
            return

        # Plot against Benford's law
        # df_leading_nums = pd.DataFrame({
        #     'Results': s_leading_nums,
        #     'Benford\'s Law': S_BENFORDS
        # })
        if 'Dem' in choice:
            color = 'b'
        elif 'Rep' in choice:
            color = 'r'
        else:
            color = 'g'
        plt.figure()
        leading_nums_plot = s_leading_nums.plot.bar(color=[color])
        leading_nums_plot.plot(range(9 if FIRST_DIGIT_TEST else 10), S_BENFORDS, '.-', color='y', markerfacecolor='w', markeredgecolor='gray')
    elif biden_v_trump:
        # Convert nums to percentages
        totals, s_leading_nums = totals_to_percentages(leading_nums, 2)

        df_leading_nums = pd.DataFrame({
            'Biden': s_leading_nums[0],
            'Trump': s_leading_nums[1],
            'Benford\'s Law': S_BENFORDS
        })
        leading_nums_plot = df_leading_nums.plot.bar(color=['b', 'r', 'gray'])
    elif all_3:
        # Convert nums to percentages
        totals, s_leading_nums = totals_to_percentages(leading_nums, 3)

        df_leading_nums = pd.DataFrame({
            'Biden': s_leading_nums[0],
            'Trump': s_leading_nums[1],
            'Jorgensen': s_leading_nums[2],
            'Benford\'s Law': S_BENFORDS
        })
        leading_nums_plot = df_leading_nums.plot.bar(color=['b', 'r', 'g', 'gray'])

    # leading_nums_plot.plot(range(9), S_BENFORDS, color='gray')
    title = 'GA {} - {} ({}) Vote Count - {:,}, Size - {:,}'.format(contest, choice, note, int(total_count), int(totals))
    ## Remove illegal characters
    for c in ('"', '/', '\\'):
        title = title.replace(c, '')
    leading_nums_plot.set_title('\n'.join(wrap(title, 60)))
    set_bl_labels(leading_nums_plot)

    if SAVE_FIGS:
        n = '{}/{}/{}.jpg'.format(dir, '1st-Digit-Test' if FIRST_DIGIT_TEST else '2nd-Digit-Test', title)
        plt.savefig(n)
        print('Saved "{}"'.format(n))
        plt.close()

def generate_leading_numbers_arr():
    return [0 for _ in range(9 if FIRST_DIGIT_TEST else 10)]

def main():
    # detail.xml - https://results.enr.clarityelections.com/GA/105369/web.264614/#/summary
    tree = ET.parse('detail.xml')
    root = tree.getroot()

    # Count leading numbers for candidates
    candidate_nums = {
        'Biden': generate_leading_numbers_arr(),
        'Trump': generate_leading_numbers_arr(),
        'Jorgensen': generate_leading_numbers_arr()
    }
    candidate_totals = {
        'Biden': None,
        'Trump': None,
        'Jorgensen': None
    }

    # Iterate all children to build dictionary
    votes = {}
    for c in root:
        # Find Contests
        if c.tag != 'Contest' or (not EXTRA_PLOTS and c.attrib['text'] != 'President of the United States'):
            continue
        # Contest key
        votes[c.attrib['text']] = {}

        # Find Choice in Contest
        for cc in c:
            if cc.tag != 'Choice':
                continue
            # Choice key
            votes[c.attrib['text']][cc.attrib['text']] = {}

            # Count leading numbers in each choice
            leading_nums = generate_leading_numbers_arr()

            # Find VoteType in Choice
            for ccc in cc:
                if ccc.tag != 'VoteType':
                    continue
                # VoteType key
                votes[c.attrib['text']][cc.attrib['text']][ccc.attrib['name']] = {}
                # Count leading numbers in each votetype
                vt_leading_nums = generate_leading_numbers_arr()
                vt_total = 0

                # Find vote by County in VoteType
                for cccc in ccc:
                    if cccc.tag != 'County':
                        continue
                    # County key to votes value
                    votes[c.attrib['text']][cc.attrib['text']][ccc.attrib['name']][cccc.attrib['name']] = cccc.attrib['votes']

                    # Get leading number
                    if (FIRST_DIGIT_TEST and int(cccc.attrib['votes']) != 0) or (not FIRST_DIGIT_TEST and int(cccc.attrib['votes']) >= 10):
                        val = int(cccc.attrib['votes'][int(not FIRST_DIGIT_TEST)])-int(FIRST_DIGIT_TEST)
                        leading_nums[val] += 1
                        vt_leading_nums[val] += 1
                        vt_total += int(cccc.attrib['votes'])
                        for n in ('Biden', 'Trump', 'Jorgensen'):
                            if n in cc.attrib['text']:
                                candidate_nums[n][val] += 1
                                candidate_totals[n] = int(cc.attrib['totalVotes'])
                                break

                # Plot votetype results, only for presidential
                if VOTETYPE_PLOTS and c.attrib['text'] == 'President of the United States':
                    print(vt_leading_nums)
                    plot_benfords_law(
                        vt_leading_nums,
                        c.attrib['text'],
                        cc.attrib['text'],
                        vt_total,
                        'By Votetype-{}'.format(ccc.attrib['name']),
                        'Presidential-Plots'
                        # 'Presidential-Plots' if c.attrib['text'] == 'President of the United States' else 'Non-Presidential-Plots'
                    )

            # Plot county results
            print(leading_nums)
            plot_benfords_law(
                leading_nums, c.attrib['text'],
                cc.attrib['text'],
                cc.attrib['totalVotes'],
                'By County',
                'Presidential-Plots' if c.attrib['text'] == 'President of the United States' else 'Non-Presidential-Plots'
            )

    # Plot Biden v Trump v Jorgensen results
    # candidate_totals = list(map(lambda x: int(x), candidate_totals))
    print(candidate_totals)
    plot_benfords_law(
        [candidate_nums[n] for n in ['Biden', 'Trump']],
        '2020 Presdential Election', 'Biden v. Trump', sum([candidate_totals[x] for x in ['Biden', 'Trump']]),
        'By County',
        'Presidential-Plots',
        biden_v_trump=True
    )
    plot_benfords_law(
        [candidate_nums[n] for n in ['Biden', 'Trump', 'Jorgensen']],
        '2020 Presidential Election', 'All candidates', sum([candidate_totals[x] for x in ['Biden', 'Trump', 'Jorgensen']]),
        'By County',
        'Presidential-Plots',
        all_3=True
    )

    if SHOW_PLOTS:
        plt.show()

if __name__=='__main__':
    main()
