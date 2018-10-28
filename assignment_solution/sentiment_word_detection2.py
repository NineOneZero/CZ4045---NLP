import inspect
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from settings import sample_review_file_loc, amazon_review_file_loc, \
    amazon_review_word_dict_loc, english_word_dict_loc, \
    filtered_amazon_review_word_dict_loc, filtered_amazon_review_word_dict_noNN_loc


"""
from assignment_solution.sentiment_word_detection2 import main
main()
"""


class KeywordItem():
    def __init__(self, keyword):
        self.keyword = keyword
        self.numReviewMentioned = 0
        self.totalScore = 0
        self.sentiment = 0
        self.adjustedSentiment = 0
        self.scoreList = []
        self.numPosMentioned = 1
        self.numNegMentioned = 1

    def __str__(self):
        return self.keyword

    def set_word_sentiment(self, numPosReview, numNegReview):
        if self.numReviewMentioned != 0:
            self.sentiment = self.totalScore / self.numReviewMentioned

        # rare words are penalized on their impact to final sentiment value
        # self.adjustedSentiment = ((2 / (1 + math.exp(-1 * self.numReviewMentioned))) - 1) * self.sentiment
        self.adjustedSentiment = self.sentiment * ((self.numPosMentioned / numPosReview) / (self.numNegMentioned / numNegReview))
        # self.adjustedSentiment = self.sentiment * ((self.numPosMentioned) / (self.numNegMentioned))

    def update_keyword_statistics(self, amazonReview):
        self.numReviewMentioned += 1
        self.totalScore += float(amazonReview.overall)
        self.scoreList.append(float(amazonReview.overall))

        if float(amazonReview.overall) >= 3:
            self.numPosMentioned += 1
        if float(amazonReview.overall) <= 2:
            self.numNegMentioned += 1


def print_iteration_progress(function_name, x):

    if x.name % 1000 == 0:
        print("{}: {} of 190919 done".format(function_name, x.name))


def sentiment_word_analysis(amazonReview):

    with open(filtered_amazon_review_word_dict_noNN_loc) as f:
        keywords = f.read().splitlines()

    keywords_dict = dict(zip([x for x in keywords],
                                [KeywordItem(x) for x in keywords]))


    numPosReview = 0
    numNegReview = 0

    for _, x in amazonReview.iterrows():
        reviewTextKeywordsList = (x.reviewText).split()
        for word in reviewTextKeywordsList:
            if word in keywords_dict:
                keywords_dict[word].update_keyword_statistics(x)

        if float(x.overall) >= 3:
            numPosReview += 1
        if float(x.overall) <= 2:
            numNegReview += 1

        print_iteration_progress(inspect.stack()[0][3], x)

    print("pos: ", numPosReview)
    print("neg: ", numNegReview)

    for _, keywordItem in keywords_dict.items():
        keywordItem.set_word_sentiment(numPosReview=numPosReview, numNegReview=numNegReview)

    # sort by adjusted sentiment
    sorted_keywordItem = sorted(keywords_dict.items(), key=lambda kv: kv[1].adjustedSentiment, reverse=True)
    positive_keyword_top20 = [x[1] for x in sorted_keywordItem[:20]]
    negative_keyword_top20 = [x[1] for x in sorted_keywordItem[-20:][::-1]]

    # plot positive keyword statistics
    plt.rcdefaults()
    fig, ax = plt.subplots()

    plt_width = 0.35

    plt_label = [x.keyword for x in positive_keyword_top20]
    plt_value_adjustedSentiment = [x.adjustedSentiment for x in positive_keyword_top20]
    plt_value_Sentiment = [x.sentiment for x in positive_keyword_top20]

    plt_y_pos = np.arange(len(plt_label))
    ax.barh(plt_y_pos+plt_width/2, plt_value_adjustedSentiment, plt_width, align='center', color='IndianRed', ecolor='black', label='adjusted sentiment')
    ax.barh(plt_y_pos-plt_width/2, plt_value_Sentiment, plt_width, align='center', color='SkyBlue', ecolor='black', label='sentiment')

    ax.set_yticks(plt_y_pos)
    ax.set_yticklabels(plt_label)
    ax.invert_yaxis()
    ax.set_xlabel('Sentiment')
    ax.set_title('Top 20 positive word ranked by calculated sentiment')
    ax.legend()

    plt.show()


    # plot negative keyword statistics
    plt.rcdefaults()
    fig, ax = plt.subplots()

    plt_width = 0.35

    plt_label = [x.keyword for x in negative_keyword_top20]
    plt_value_adjustedSentiment = [x.adjustedSentiment for x in negative_keyword_top20]
    plt_value_Sentiment = [x.sentiment for x in negative_keyword_top20]

    plt_y_pos = np.arange(len(plt_label))
    ax.barh(plt_y_pos+plt_width/2, plt_value_adjustedSentiment, plt_width, align='center', color='IndianRed', ecolor='black', label='adjusted sentiment')
    ax.barh(plt_y_pos-plt_width/2, plt_value_Sentiment, plt_width, align='center', color='SkyBlue', ecolor='black', label='sentiment')

    ax.set_yticks(plt_y_pos)
    ax.set_yticklabels(plt_label)
    ax.invert_yaxis()
    ax.set_xlabel('Sentiment')
    ax.set_title('Top 20 negative word ranked by calculated sentiment')
    ax.legend()

    plt.show()


def clean_amazon_review_df(df):
    """ clean dataframe of amazon review """
    # df = pd.read_json('SampleReview.json', lines=True)

    def clean_review_text(x):
        text = x.reviewText.lower()

        # remove url
        regex = r"https?\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?"
        text = re.sub(regex, "", text, 0)

        # add spaces between digit and alphabet
        text = re.sub(r'\b(\d+)([a-z]+)\b', r'\g<1> \g<2>', text, 0)

        # remove number, comma-formatted number and float number e.g. 100,000 & 10.12
        text = re.sub(r'\b\d+(,\d+)*(\.\d*)?\b', "", text, 0)

        # convert negation word and following word into single token "not good" => not_good
        text = re.sub(r'\b(no|not)\b\s+(\b\w+\b)', "\g<1>_\g<2>", text, 0)

        # remove stopwords
        tokenizer = RegexpTokenizer(r'\w+')
        word_list = tokenizer.tokenize(text)
        filtered_words = [word for word in word_list if word not in stopwords.words('english')]

        x.reviewText = " ".join(filtered_words)
        print_iteration_progress(inspect.stack()[0][3], x)

        return x

    cleaned_df = df.apply(lambda x: clean_review_text(x), axis=1)
    del df
    return cleaned_df


def build_amazon_keyword_dictionary(df):
    """ build amazon keyword dictionary from review text """

    keyword_list = set()
    for _, x in df.iterrows():
        keyword_list = keyword_list | set(x.reviewText.split())
        print_iteration_progress(inspect.stack()[0][3], x)

    keyword_list = list(keyword_list)
    keyword_list = sorted(keyword_list)
    keywords_to_write = "\n".join(keyword_list)

    # replace words starting with numbers
    keywords_to_write = re.sub(re.compile(r'^\b\d+.*\b\n', re.MULTILINE), "", keywords_to_write)

    with open(amazon_review_word_dict_loc, 'a') as keyword_file:
        keyword_file.write(keywords_to_write)


def build_filtered_amazon_keyword_dictionary():
    """ filter the built review keyword dictionary by valid english word """

    with open(amazon_review_word_dict_loc) as f:
        amazon_keywords = f.read().splitlines()

    with open(english_word_dict_loc) as f:
        english_words = f.read().splitlines()

    filtered_keywords = [x for x in amazon_keywords if x in english_words]
    keywords_to_write = "\n".join(filtered_keywords)

    with open(filtered_amazon_review_word_dict_loc, 'a') as keyword_file:
        keyword_file.write(keywords_to_write)


def build_filtered_amazon_keyword_dictionary_noNN():
    """ filter noun term from the review keyword dictionary """
    import nltk
    nltk.download('averaged_perceptron_tagger')
    from nltk import pos_tag

    with open(filtered_amazon_review_word_dict_loc) as f:
        filtered_keywords = f.read().splitlines()

    keywords_noNN = [x for x in filtered_keywords if pos_tag([x])[0][1] != 'NN']
    keywords_to_write = "\n".join(keywords_noNN)

    with open(filtered_amazon_review_word_dict_noNN_loc, 'a') as keyword_file:
        keyword_file.write(keywords_to_write)


def main():

    # clean amazon review text of stopwords
    df = pd.read_json(amazon_review_file_loc, lines=True)
    df = clean_amazon_review_df(df)

    # create keyword dictionary for sentiment analysis
    build_amazon_keyword_dictionary(df)
    build_filtered_amazon_keyword_dictionary()
    build_filtered_amazon_keyword_dictionary_noNN()
