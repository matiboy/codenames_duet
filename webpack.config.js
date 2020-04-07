const path = require('path');
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = {
  entry: {
    chime: './src/chime.ts',
    game_split: './src/game_split.ts'
  },
  output: {
    filename: '[name].js',
    library: ['CovidNames', '[name]'],
    path: path.resolve(__dirname, 'static'),
  },
  devtool: 'inline-source-map',
  module: {
    rules: [
      {
        test: /\.ts$/,
        loader: 'ts-loader',
        exclude: /node_modules/,
        options: {
          appendTsSuffixTo: [/\.vue$/],
        }
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        exclude: /node_modules/,
      },
    ],
  },
  performance: {
    hints: false
  },
  plugins: [
    new VueLoaderPlugin()
  ],
  resolve: {
    extensions: [ '.ts', '.js', '.vue' ],
  },
};