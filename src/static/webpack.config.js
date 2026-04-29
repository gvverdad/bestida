// https://github.com/bradtraversy/webpack-starter/blob/main/webpack.config.js

const path = require('path')

module.exports = (env, argv) => {
    return {
        entry: {
            app: path.resolve(__dirname, './js/app.js'),
        },
        output: {
            path: path.resolve(__dirname, 'dist'),
            filename: "[name].bundle.js",
            clean: true
        },
        mode: 'development',
        devtool: 'source-map',      // maps are exposed
        //mode: 'production',
        //devtool: "hidden-source-map", // do not expose maps
        //optimization: {
        //    minimize: true,
        //},
        module: {
            rules: [
                {
                    test: /\.css$/,
                    use: ['style-loader', 'css-loader', 'sass-loader',
                            {
                                loader: 'postcss-loader',
                                options: {
                                    postcssOptions: {
                                        plugins: ['postcss-preset-env'],
                                    },
                                },
                            },
                    ],
                },

            ],
        },
        stats: {
            errorDetails: true,
            children: true
        },
    };
};
