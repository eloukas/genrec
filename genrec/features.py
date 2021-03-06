import librosa
import numpy as np
#np.set_printoptions(threshold=np.nan)

from genrec.logger import get_logger
from genrec.utils import chunks

class FeatureExtractor:
    def __init__(self, sr=22050, fft_len=512):
        self.target_sr = sr
        self.fft_len = fft_len

        self.logger = get_logger('ft-extractor')

    def extract_fv(self, sig, sr=22050):
        """ Extracts the features from a signal """
        sig = self._preprocess_signal(sig, sr)

        # Keep only not silent windows
        fvs = [ fv for fv in self.timbral(sig) if fv ]
        return np.mean(fvs, axis=0)

    def extract_fvs(self, sig, sr=22050):
        """ Extracts the features from a signal every 1 second """
        sig = self._preprocess_signal(sig, sr)
        yield from self.timbral(sig)

    def timbral(self, sig):
        """ Extracts the timbral features from a signal """
        # 43 analysis windows * 512 samples = 22016 ~= 22050 (--> 1 sec)
        # NOTE: previous results used 40 analysis windows * 512 samples = 20480 samples
        for i, tex_wnd in enumerate(chunks(sig, self.target_sr)):
            if len(tex_wnd) < self.fft_len:
                continue

            fv = TimbralFeatures(
                tex_wnd,
                sr=self.target_sr,
            ).fv()

            if any(np.isnan(fv)):
                self.logger.warning('NaN value found in fv[{}] = \n{}'.format(i, fv))
                yield [ ]
                continue

            yield fv

    def _preprocess_signal(self, sig, sr):
        if sr != self.target_sr:
            # resample to target sampling rate
            # NOTE: scale=True so total energy is ~same for both signals
            sig = librosa.resample(sig, sr, self.target_sr, scale=True)

        return self._strip_signal(sig)

    def _strip_signal(self, sig):
        """ Strip zero-valued samples at start/end of the signal """

        start = 0
        while sig[start] == b'0':
            start += 1

        end = len(sig) - 1
        while sig[end] == b'0':
            end -= 1

        return sig[start:end]


class TimbralFeatures:
    features = ['centroid', 'rolloff', 'flux', 'zero_crossings', 'mfcc', 'low_energy']

    def __init__(self, tex_wnd, fft_len=512, sr=22050):
        self.tex_wnd = tex_wnd
        self.an_wnd_len = fft_len
        self.sr = sr

        # calc signal spectrum
        self.fft_tex_wnds = np.abs(
            librosa.stft(
                y=tex_wnd,
                n_fft=fft_len,
                hop_length=fft_len,
            )
        )

    def centroid(self):
        """
        Calculate the spectral centroid for each analysis window

        Returns the mean and variance
        """

        centroids = librosa.feature.spectral_centroid(
            S=self.fft_tex_wnds
        ).ravel()
        return np.mean(centroids), np.std(centroids)


    def rolloff(self):
        """
        Calculate the roll-off frequency for each analysis window

        Returns the mean and variance
        """

        rolloffs = librosa.feature.spectral_rolloff(
            S=self.fft_tex_wnds
        ).ravel()
        return np.mean(rolloffs), np.std(rolloffs)


    def flux(self):
        """
        Calculate the spectral flux for each analysis window

        Returns the mean and variance
        """

        fft_tex_wnds_T = self.fft_tex_wnds.T
        w_nrg = librosa.feature.rmse(
            S=self.fft_tex_wnds,
            frame_length=self.an_wnd_len,
            hop_length=self.an_wnd_len
        ).ravel()

        # normalize via energy
        for i in range(len(fft_tex_wnds_T)):
            fft_tex_wnds_T[i] /= w_nrg[i]

        fluxes = np.empty(
            shape=(len(fft_tex_wnds_T) - 1,),
            dtype=np.float64,
        )
        for i in range(1, len(fft_tex_wnds_T)):
            fluxes[i-1] = np.sum(
                (fft_tex_wnds_T[i-1] - fft_tex_wnds_T[i]) ** 2
            )

        return np.mean(fluxes), np.std(fluxes)


    def zero_crossings(self):
        """
        Calculate the perc of zero crossings for each analysis window

        Returns the mean and variance
        """

        zc = librosa.feature.zero_crossing_rate(
            y=self.tex_wnd,
            frame_length=self.an_wnd_len,
            hop_length=self.an_wnd_len,
        ).ravel()
        return np.mean(zc), np.std(zc)


    def mfcc(self, n_mfcc=5):
        """
        Calculate the first 'n_mfcc' MFCCs for each analysis window

        Returns the mean and variance
        """

        mfccs = librosa.feature.mfcc(
            S=self.fft_tex_wnds,
            frame_length=self.an_wnd_len,
            hop_length=self.an_wnd_len,
            n_mfcc=n_mfcc,
        )

        return (*np.mean(mfccs, axis=1), *np.std(mfccs, axis=1))


    def low_energy(self):
        """
        Returns the perc of analysis windows which have energy
        less than the mean energy of this texture window
        """

        w_nrg = librosa.feature.rmse(
            S=self.fft_tex_wnds,
            frame_length=self.an_wnd_len,
            hop_length=self.an_wnd_len
        ).ravel()
        avg_nrg = np.mean(w_nrg)

        return (np.sum(
            [ nrg < avg_nrg for nrg in w_nrg ]
        ) / len(w_nrg),)


    def fv(self):
        """
        Return the resulting feature vector of this texture window
        """
        features = map(lambda f: getattr(self, f), self.features)

        fv = [ ]
        for ft in features:
            fv.extend( ft() )

        return fv

