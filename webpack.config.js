const path = require('path');

module.exports = {
  entry: './apps/web/assets/app.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'apps/web/static')
  },
  devtool: 'source-map',
  performance: {
    hints: false,
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/i,
        loader: 'babel-loader',
      },
      {
        test: /\.(scss)$/,
        use: [{
          loader: 'style-loader'
        }, {
          loader: 'css-loader'
        }, {
          loader: 'postcss-loader',
          options: {
            postcssOptions: {
              plugins: function () {
                return [
                  require('autoprefixer')
                ];
              }
            }
          }
        }, {
          loader: 'sass-loader'
        }]
      }
    ]
  }
};
