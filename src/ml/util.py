import pandas as pd
from matplotlib import pyplot as plt


def extract_text_model(urls):
    char2idx = {}
    max_url_seq_length = 0
    for url in urls:
        max_url_seq_length = max(max_url_seq_length, len(url))
        for ch in url:
            if ch not in char2idx:
                char2idx[ch] = len(char2idx)

    n_input_tokens = len(char2idx)
    idx2char = dict([(idx, ch) for ch, idx in char2idx.items()])
    return {
        'n_input_tokens': n_input_tokens,
        'char2idx': char2idx,
        'idx2char': idx2char,
        'max_url_seq_length': max_url_seq_length
    }


def load_url_data(data_dir_path):
    df = pd.read_csv(data_dir_path / 'malicious_urls' / 'data.csv', sep=',', header=0)
    df = pd.DataFrame({'url': df['url'], 'label': df['label'].apply(lambda x: int(x == 'bad'))})
    return df.sample(frac=1).reset_index(drop=True)


def merge_dict(dict1, dict2):
    merged = dict1.copy()
    for key, value in dict2.items():
        if value is not None:
            merged[key] = value

    return merged


def plot_history_2win(history):
    plt.subplot(211)
    plt.title('Accuracy')
    plt.plot(history.history['acc'], color='g', label='Train')
    plt.plot(history.history['val_acc'], color='b', label='Validation')
    plt.legend(loc='best')

    plt.subplot(212)
    plt.title('Loss')
    plt.plot(history.history['loss'], color='g', label='Train')
    plt.plot(history.history['val_loss'], color='b', label='Validation')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()


def create_history_plot(history, model_name):
    plt.title('Accuracy and Loss (' + model_name + ')')
    plt.plot(history.history['acc'], color='g', label='Train Accuracy')
    plt.plot(history.history['val_acc'], color='b', label='Validation Accuracy')
    plt.plot(history.history['loss'], color='r', label='Train Loss')
    plt.plot(history.history['val_loss'], color='m', label='Validation Loss')
    plt.legend(loc='best')
    plt.tight_layout()


def plot_history(history, model_name):
    create_history_plot(history, model_name)
    plt.show()


def plot_and_save_history(history, model_name, file_path):
    create_history_plot(history, model_name)
    plt.savefig(file_path)
