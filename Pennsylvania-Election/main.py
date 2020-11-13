import pandas as pd
import matplotlib.pyplot as plt
from textwrap import wrap

SHOW_PLOTS = True # Show interactive plot
SAVE_FIGS = False # Save jpg of plot
MAIL_PLOTS = True # Show mail vote plots
PROVISIONAL_PLOTS = True # Show provisional vote plots
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
    s_leading_nums = [None for _ in range(length)]
    # Convert nums to percentages
    for i in range(length):
        tot_nums = sum(leading_nums[i])
        totals += tot_nums
        s_leading_nums[i] = pd.Series(
            map(lambda x: x / tot_nums, leading_nums[i]),
            index=range(1,10) if FIRST_DIGIT_TEST else range(0,10)
        )

    return totals, s_leading_nums

def set_bl_labels(p):
    p.set_xlabel('{} Digit Value'.format('Leading' if FIRST_DIGIT_TEST else 'Second'))
    p.set_ylabel('Proportion')

def save_plot(name):
    n = 'Presidential-Plots/{}/'.format('1st-Digit-Test' if FIRST_DIGIT_TEST else '2nd-Digit-Test')+name+'.jpg'
    plt.savefig(n)
    print('Saved "{}"'.format(n))
    plt.close()

def plot_benfords_law(df, colors=['b', 'r', 'g', 'gray']):
    p = df.plot.bar(color=colors, rot=45)
    set_bl_labels(p)
    return p

def plot_results(leading_nums, s_leading_nums, total_votes, type):
    # Plot each candidate results
    for i, c in enumerate(leading_nums):
        if c == 'BIDEN':
            color = 'b'
        elif c == 'TRUMP':
            color = 'r'
        elif c=='JORGENSEN':
            color = 'g'
        plt.figure()
        p = plot_benfords_law(s_leading_nums[i], colors=[color])
        p.plot(range(len(S_BENFORDS)), S_BENFORDS, '.-', color='y', markerfacecolor='w', markeredgecolor='gray')
        p.legend(['Benford\'s law', 'Actual value'])
        title = 'PA 2020 Presidential Election ({}) - {} Vote Count - {:,}, Size - {:,}'.format(type, c, total_votes[c], sum(leading_nums[c]))
        p.set_title('\n'.join(wrap(title, 60)))

        if SAVE_FIGS:
            save_plot(title)

def generate_leading_numbers_arr():
    return [0 for _ in range(9 if FIRST_DIGIT_TEST else 10)]

def main():
    df = pd.read_csv('pennsylvania_county_votes.csv')[['County Name', 'Candidate Name', 'Votes', 'Mail Votes', 'Provisional Votes']]
    # print(df.head())

    # Get leading numbers of each candidate
    leading_nums = {
        'BIDEN': generate_leading_numbers_arr(),
        'TRUMP': generate_leading_numbers_arr(),
        'JORGENSEN': generate_leading_numbers_arr()
    }
    total_votes = {
        'BIDEN': 0,
        'TRUMP': 0,
        'JORGENSEN': 0
    }
    if MAIL_PLOTS:
        leading_mail_nums = {
            'BIDEN': generate_leading_numbers_arr(),
            'TRUMP': generate_leading_numbers_arr(),
            'JORGENSEN': generate_leading_numbers_arr()
        }
        total_mail_votes = {
            'BIDEN': 0,
            'TRUMP': 0,
            'JORGENSEN': 0
        }
        leading_not_mail_nums = {
        'BIDEN': generate_leading_numbers_arr(),
        'TRUMP': generate_leading_numbers_arr(),
        'JORGENSEN': generate_leading_numbers_arr()
        }
        total_not_mail_votes = {
        'BIDEN': 0,
        'TRUMP': 0,
        'JORGENSEN': 0
        }
    if PROVISIONAL_PLOTS:
        leading_prov_nums = {
            'BIDEN': generate_leading_numbers_arr(),
            'TRUMP': generate_leading_numbers_arr(),
            'JORGENSEN': generate_leading_numbers_arr()
        }
        total_prov_votes = {
            'BIDEN': 0,
            'TRUMP': 0,
            'JORGENSEN': 0
        }

    def count_votes(votes, leading_nums, total_votes, name):
        votes = votes.replace(',', '')
        if (FIRST_DIGIT_TEST and int(votes) != 0) or (not FIRST_DIGIT_TEST and int(votes) >= 10):
            leading_nums[name][int(votes[int(not FIRST_DIGIT_TEST)])-int(FIRST_DIGIT_TEST)] += 1
            total_votes[name] += int(votes.replace(',', ''))

    for _, r in df.iterrows():
        for name in ['BIDEN', 'TRUMP', 'JORGENSEN', 'err']:
            if name == 'err':
                raise Exception('Unknown candidate name')
            if name in r['Candidate Name']:
                count_votes(r['Votes'], leading_nums, total_votes, name)
                if MAIL_PLOTS:
                    count_votes(r['Mail Votes'], leading_mail_nums, total_mail_votes, name)
                    r_not_mail_votes = pd.to_numeric(r['Votes'].replace(',',''))-pd.to_numeric(r['Mail Votes'].replace(',',''))-pd.to_numeric(r['Provisional Votes'].replace(',',''))
                    count_votes(str(r_not_mail_votes), leading_not_mail_nums, total_not_mail_votes, name)
                if PROVISIONAL_PLOTS:
                    count_votes(r['Provisional Votes'], leading_prov_nums, total_prov_votes, name)
                break

    # print(leading_nums)
    # print(leading_mail_nums)
    # print(leading_prov_nums)
    # print(leading_not_mail_nums)

    # Convert counts to percentages
    def counts_to_percentages(leading_nums):
        return totals_to_percentages(
            [leading_nums['BIDEN'], leading_nums['TRUMP'], leading_nums['JORGENSEN']],
            3
        )
    totals, s_leading_nums = counts_to_percentages(leading_nums)
    if MAIL_PLOTS:
        mail_totals, s_leading_mail_nums = counts_to_percentages(leading_mail_nums)
        not_mail_totals, s_leading_not_mail_nums = counts_to_percentages(leading_not_mail_nums)
    if PROVISIONAL_PLOTS:
        prov_totals, s_leading_prov_nums = counts_to_percentages(leading_prov_nums)

    # Plot individual results
    plot_results(leading_nums, s_leading_nums, total_votes, 'All Votes')
    if MAIL_PLOTS:
        plot_results(leading_mail_nums, s_leading_mail_nums, total_mail_votes, 'Mail Ballots')
        plot_results(leading_not_mail_nums, s_leading_not_mail_nums, total_not_mail_votes, 'Not Mail Ballots')
    if PROVISIONAL_PLOTS:
        plot_results(leading_prov_nums, s_leading_prov_nums, total_prov_votes, 'Provisional Ballots')

    # Plot candidate results against each other
    df_leading_nums = pd.DataFrame({
        'Biden': s_leading_nums[0],
        'Trump': s_leading_nums[1],
        'Jorgensen': s_leading_nums[2],
        'Benford\'s Law': S_BENFORDS
    })
    p = plot_benfords_law(df_leading_nums)
    title = '2020 Presdential Election (All Votes) - All candidates Vote Count - {:,}, Size - {:,}'.format(
        sum([total_votes[c] for c in ['BIDEN', 'TRUMP', 'JORGENSEN']]),
        sum([sum(leading_nums[a]) for a in ['BIDEN', 'TRUMP', 'JORGENSEN']])
    )
    p.set_title('\n'.join(wrap(title, 60)))
    if SAVE_FIGS:
        save_plot(title)

    df_leading_nums = pd.DataFrame({
        'Biden': s_leading_nums[0],
        'Trump': s_leading_nums[1],
        'Benford\'s Law': S_BENFORDS
    })
    p = plot_benfords_law(df_leading_nums, colors=['b', 'r', 'gray'])
    title = '2020 Presdential Election (All Votes) - Biden v. Trump Vote Count - {:,}, Size - {:,}'.format(
        sum([total_votes[c] for c in ['BIDEN', 'TRUMP']]),
        sum([sum(leading_nums[a]) for a in ['BIDEN', 'TRUMP']])
    )
    p.set_title('\n'.join(wrap(title, 60)))
    if SAVE_FIGS:
        save_plot(title)

    # Print totals
    sum_vote_counts = 0
    for c in ['BIDEN', 'TRUMP', 'JORGENSEN']:
        sum_vote_counts += total_votes[c]

    for c in ['BIDEN', 'TRUMP', 'JORGENSEN']:
        print('{:<9} : {:%} ({:,})'.format(c, total_votes[c]/sum_vote_counts, total_votes[c]))

    if SHOW_PLOTS:
        plt.show()

if __name__=='__main__':
    main()
