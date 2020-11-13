import pandas as pd
import matplotlib.pyplot as plt
import json
import math
from textwrap import wrap

SHOW_PLOTS = True # Show interactive plots
SAVE_FIGS = False # Save jpg of plots
NATIONWIDE_COUNTS_PLOTS = True # Plots of nationwide counts by county
STATE_COUNTY_COUNTS_PLOTS = True # Plots of counts at STATES_TO_RUN states by county
STATE_COUNTS_PLOTS = False # Plots of counts at the 50 states
CANDIDATES_TO_RUN = [('Biden', ['b', 'c']), ('Trump', ['r', 'orange']), ('Jorgensen', ['g', 'c'])] # (Which candidate to count, color)
FIRST_DIGIT_TEST = False # 1st or 2nd digit to do Benford's test on
FINAL_DIGITS_TEST = False # Test last 2 digits
STATES_TO_RUN = [ # Which states to count
    "AK",
    "AL",
    "AR",
    "AZ",
    "CA",
    "CO",
    "CT",
    "DC",
    "DE",
    "FL",
    "GA",
    "HI",
    "IA",
    "ID",
    "IL",
    "IN",
    "KS",
    "KY",
    "LA",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MS",
    "MT",
    "NC",
    "ND",
    "NE",
    "NH",
    "NJ",
    "NM",
    "NV",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VA",
    "VT",
    "WA",
    "WI",
    "WV",
    "WY"
]

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

def get_digit(num):
    return int(str(num)[0 if FIRST_DIGIT_TEST else 1])

def get_last_digit(num):
    return int(str(num)[-1])
def get_plast_digit(num):
    return int(str(num)[-2])

def set_bl_labels(p):
    p.set_xlabel('{} Digit Value'.format('Leading' if FIRST_DIGIT_TEST else 'Second'))
    p.set_ylabel('Proportion')
    p.legend(['Benford\'s law', 'Actual value'])

def save_plot_jpg(name):
    n = '{}-Digit-BL-Test/{}'.format(
        '1st' if FIRST_DIGIT_TEST else '2nd', name
    )
    plt.savefig(n)
    print('Saved "{}"'.format(n))
    plt.close()

def plot_benfords_law(data, vote_totals, title, colors, save_dir):
    # Convert to percentages
    data_totals = sum(data)
    data = pd.Series(map(lambda x: x / data_totals, data), index=range(1,10) if FIRST_DIGIT_TEST else range(0,10))
    # Plot with Benford's law
    plt.figure()
    p = data.plot.bar(color=colors, rot=45)
    p.plot(range(len(S_BENFORDS)), S_BENFORDS, '.-', color='y', markerfacecolor='w', markeredgecolor='gray')
    title = '{} Vote Count - {:,}, Size - {:,}'.format(title, vote_totals , data_totals)
    p.set_title('\n'.join(wrap(title, 60)))
    set_bl_labels(p)

    if SAVE_FIGS:
        if save_dir:
            name = 'State-Counts-by-county-jpgs/'+title+'.jpg'
        else:
            name = 'Nationwide-Counts-by-county-jpgs/'+title+'.jpg'
        save_plot_jpg(name)

    return data

def find_key(l, k):
    if type(k) == tuple:
        # Find matching key in a list by iterating
        if type(l) == list:
            for v in l:
                if v[k[0]] == k[1]:
                    # print(v)
                    return v
            raise Exception('Key not found in list ({})'.format(k[0]))
        # Find matching key in a dict by comparison
        elif type(l) == dict:
            if k[0] not in l:
                raise Exception('Key not found in dict ({})'.format(k[0]))
            if l[k[0]] != k[1]:
                return False
            return l
        else:
            raise Exception('Unexpected type ({})'.format(type(l)))
    else:
        return l[k]

def count_leading_numbers_and_plot(data, keys, title, colors=['b'], state=None):
    leading_nums = [0 for _ in range(9 if FIRST_DIGIT_TEST else 10)]
    last_digit_totals = [0 for _ in range(10)]
    plast_digit_totals = [0 for _ in range(10)]
    totals = 0
    for val in data:
        # Get current key value
        curr_val = find_key(val, keys[0])
        if curr_val == False:
            continue
        if len(keys) > 1:
            for i in range(1, len(keys)):
                curr_val = find_key(curr_val, keys[i])

        # Count leading digit and total vote count
        if (FIRST_DIGIT_TEST and int(curr_val) != 0) or (not FIRST_DIGIT_TEST and int(curr_val) >= 10):
            digit = get_digit(curr_val)
            if FIRST_DIGIT_TEST:
                digit -= 1 # Shift 1 for 1st digit test (no 0 value)
            leading_nums[digit] += 1
            totals += int(curr_val)

        # Final digits count
        if FINAL_DIGITS_TEST and int(curr_val) != 0:
            last_digit_totals[get_last_digit(curr_val)] += 1
            if int(curr_val) >= 10:
                plast_digit_totals[get_plast_digit(curr_val)] += 1

    if FINAL_DIGITS_TEST:
        print(last_digit_totals)
        print(plast_digit_totals)
        df = pd.DataFrame({
            'Last Digit': last_digit_totals,
            'Second Last Digit': plast_digit_totals
        })
        p = df.plot.bar(color=colors, edgecolor='k')
        mean_l_d = df['Last Digit'].mean()
        mean_pl_d = df['Second Last Digit'].mean()
        p.hlines(mean_l_d, -1, 10, linestyles='dashed', color='k')
        p.hlines(mean_pl_d, -1, 10, linestyles='dashed', color='gray')
        p.legend(['Mean Last Digit', 'Mean 2nd Last Digit', 'Last Digit', 'Second Last Digit'])
        f_title = title+'2 Final Digits'
        p.set_title('\n'.join(wrap(f_title, 60)))
        p.set_xlabel('Number')
        p.set_ylabel('Frequency')

        if SAVE_FIGS:
            if state:
                name = 'Final-Digits-Test/State-Counts-by-county-jpgs/'+f_title+'.jpg'
            else:
                name = 'Final-Digits-Test/Nationwide-Counts-by-county-jpgs/'+f_title+'.jpg'
            plt.savefig(name)
            print('Saved "{}"'.format(name))
            plt.close()

    return totals, sum(leading_nums), plot_benfords_law(leading_nums, totals, title, colors[0], state)

def main():
    with open('counties_president.json') as f:
        election_data = json.load(f)

    county_data = election_data['map_county_data']['election']['race']
    state_data = election_data['top_level_ru']

    # Count leading numbers
    if NATIONWIDE_COUNTS_PLOTS:
        nationwide_leading_numbers = {x : None for x, _ in CANDIDATES_TO_RUN}
        nationwide_totals = 0
        nationwide_leading_nums_totals = 0
    if STATE_COUNTY_COUNTS_PLOTS:
        state_county_leading_numbers = {x : {y : None for y, _ in CANDIDATES_TO_RUN} for x in STATES_TO_RUN}
        state_county_totals = {x : 0 for x in STATES_TO_RUN}
        state_county_leading_nums_totals = {x : 0 for x in STATES_TO_RUN}

    # Count and plot individual candidate leading numbers
    for candidate, color in CANDIDATES_TO_RUN:

        # Count all counties in the US
        if NATIONWIDE_COUNTS_PLOTS:
            nationwide_totals, nationwide_leading_nums_totals, nationwide_leading_numbers[candidate] = count_leading_numbers_and_plot(
                county_data,
                ['candidates', ('last_name', candidate), 'votes'],
                '{} 2020 Election {} by County, '.format('All Votes', candidate),
                colors=color
            )

        # Count in certain states
        if STATE_COUNTY_COUNTS_PLOTS:
            for state in STATES_TO_RUN:
                tot, ln_tot, state_county_leading_numbers[state][candidate] = count_leading_numbers_and_plot(
                    county_data,
                    [('region_key', state), 'candidates', ('last_name', candidate), 'votes'],
                    '{} 2020 Election {} by County, '.format(state, candidate),
                    colors=color,
                    state=state
                )
                state_county_totals[state] += tot
                state_county_leading_nums_totals[state] += ln_tot

        # Count state level
        if STATE_COUNTS_PLOTS:
            count_leading_numbers_and_plot(
                state_data,
                ['candidates', ('last_name', candidate), 'votes'],
                '2020 Election {} by State, '.format(candidate),
                colors=color
            )

    def plot_combined_counts(df, biden_v_trump):
        return pd.DataFrame(df).plot.bar(
            color=['b', 'r', 'gray'] if biden_v_trump else ['b', 'r', 'g', 'gray'],
            rot=45
        )

    # Plot canididates datas on same figure
    if NATIONWIDE_COUNTS_PLOTS:
        nationwide_leading_numbers['Benford\'s Law'] = S_BENFORDS
        # Plot all 3, and biden v trump
        for caption, biden_v_trump in [('All Candidates', False), ('Biden v. Trump', True)]:
            # If biden_v_trump, reduce to only those 2 candidates
            if biden_v_trump:
                # If already biden_v_trump, skip
                if len(nationwide_leading_numbers) == 3:
                    continue
                nationwide_leading_numbers = {x : nationwide_leading_numbers[x] for x in ['Biden', 'Trump', 'Benford\'s Law']}
            p = plot_combined_counts(nationwide_leading_numbers, biden_v_trump)
            title = 'All votes 2020 Election {} by County, Vote Count - {:,}, Size - {:,}'.format(
                caption,
                nationwide_totals,
                nationwide_leading_nums_totals
            )
            p.set_title('\n'.join(wrap(title, 60)))
            set_bl_labels(p)
            if SAVE_FIGS:
                name = 'Nationwide-Counts-by-county-jpgs/Combined '+title+'.jpg'
                save_plot_jpg(name)

    if STATE_COUNTY_COUNTS_PLOTS:
        for state in STATES_TO_RUN:
            # Plot all 3, and biden v trump
            for caption, biden_v_trump in [('All Candidates', False), ('Biden v. Trump', True)]:
                # If biden_v_trump, reduce to only those 2 candidates
                if biden_v_trump:
                    # If already biden_v_trump, skip
                    if len(state_county_leading_numbers[state]) == 3:
                        continue
                    state_county_leading_numbers[state] = {x : state_county_leading_numbers[state][x] for x in ['Biden', 'Trump', 'Benford\'s Law']}
                state_county_leading_numbers[state]['Benford\'s Law'] = S_BENFORDS
                p = plot_combined_counts(state_county_leading_numbers[state], biden_v_trump)
                title = '{} 2020 Election {} by County, Vote Count - {:,}, Size - {:,}'.format(
                    state,
                    caption,
                    state_county_totals[state],
                    state_county_leading_nums_totals[state]
                )
                p.set_title('\n'.join(wrap(title, 60)))
                set_bl_labels(p)
                if SAVE_FIGS:
                    name = 'State-Counts-by-county-jpgs/Combined-Plots/'+title+'.jpg'
                    save_plot_jpg(name)

    plt.show()

if __name__=='__main__':
    main()
