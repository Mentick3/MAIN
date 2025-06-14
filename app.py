 
from tkinter import ttk, messagebox
import pandas
import talib
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StockSignalApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Stock Signal App")
        self.root.geometry("800x600")

        self.label = ttk.Label(root, text="Stock Signal Generator", font=('Arial', 16))
        self.label.pack(pady=10)

        self.symbol_entry = ttk.Entry(root, width=20)
        self.symbol_entry.insert(0, "NSE:NIFTY50")
        self.symbol_entry.pack(pady=5)

        self.fetch_button = ttk.Button(root, text="Fetch Signals", command=self.fetch_signals)
        self.fetch_button.pack(pady=5)

        self.signal_text = tk.Text(root, height=10, width=80)
        self.signal_text.pack(pady=10)

        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

    def fetch_signals(self):
        try:
            symbol = self.symbol_entry.get()
            self.signal_text.delete(1.0, tk.END)
            self.signal_text.insert(tk.END, "Fetching data and generating signals...\n")
            
            df = self.get_sample_data(symbol)
            signals = self.generate_signals(df)
            self.signal_text.insert(tk.END, "Signals:\n")
            for signal in signals:
                self.signal_text.insert(tk.END, f"• {signal}\n")

            self.plot_data(df)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_sample_data(self, symbol):
        ticker = symbol.split(":")[-1]
        if ticker == "NIFTY50":
            ticker = "^NSEI"
        df = yf.download(ticker, period="1mo", interval="1d")
        df['ADX'] = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['RSI'] = talib.RSI(df['Close'], timeperiod=14)
        df['MACD'], _, _ = talib.MACD(df['Close'])
        upper, middle, lower = talib.BBANDS(df['Close'], timeperiod=20)
        df['BB_upper'] = upper
        df['BB_lower'] = lower
        return df

    def generate_signals(self, df):
        signals = []
        last_row = df.iloc[-1]
        if last_row['ADX'] > 25:
            if last_row['Close'] > last_row['BB_upper']:
                signals.append("Overbought (BB)")
            elif last_row['Close'] < last_row['BB_lower']:
                signals.append("Oversold (BB)")
        if last_row['RSI'] > 70:
            signals.append("Overbought (RSI)")
        elif last_row['RSI'] < 30:
            signals.append("Oversold (RSI)")
        return signals

    def plot_data(self, df):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(df.index, df['Close'], label='Close')
        ax.plot(df.index, df['BB_upper'], label='BB Upper', linestyle='--')
        ax.plot(df.index, df['BB_lower'], label='BB Lower', linestyle='--')
        ax.legend()
        ax.set_title("Price with Bollinger Bands")
        self.canvas.draw()

if _name_ == "_main_":
    root = tk.Tk()
    app = StockSignalApp(root)
    root.mainloop()
