const path = require('path');

module.exports = {
  entry: './src/chime.ts',
  output: {
    filename: 'chime.js',
    path: path.resolve(__dirname, 'static'),
  },
  devtool: 'inline-source-map',
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: [ '.ts', '.js' ],
  },
};