#include <bits/stdc++.h>
#include <sys/resource.h>
using namespace std;
#ifdef MASPY
#include "my_template.hpp"
#include "mod/modint.hpp"
#include "poly/2d/fps_inv_2d.hpp"
#include "poly/2d/fps_log_2d.hpp"
#include "poly/2d/fps_exp_2d.hpp"
using Mint = modint998;
#else
#include "modint/montgomery-modint.hpp"
#include "fps/ntt-friendly-fps.hpp"
#include "fps/multivariate-fps.hpp"
using Mint = LazyMontgomeryModInt<998244353>;
#endif

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int width, height;
    long long exponent;
    std::string operation;
    std::cin >> width >> height >> operation >> exponent;
    int warmups = argc > 1 ? std::stoi(argv[1]) : 0;
#ifdef MASPY
    std::vector<std::vector<Mint>> input(height, std::vector<Mint>(width));
    for (auto& row : input) for (auto& x : row) { int value; std::cin >> value; x = value; }
    auto calculate = [&]() {
        if (operation == "inverse") return fps_inv_2d(input);
        if (operation == "logarithm") return fps_log_2d(input);
        if (operation == "exponential") return fps_exp_2d(input);
        auto values = fps_log_2d(input);
        for (auto& row : values) for (auto& x : row) x *= Mint(exponent);
        return fps_exp_2d(values);
    };
#else
    using Series = MultivariateFormalPowerSeries<Mint>;
    FormalPowerSeries<Mint> values(width * height);
    for (auto& x : values) { int value; std::cin >> value; x = value; }
    Series input(values, {width, height});
    auto calculate = [&]() {
        if (operation == "inverse") return input.inv();
        if (operation == "logarithm") return input.log();
        if (operation == "exponential") return input.exp();
        return input.pow(exponent);
    };
#endif
    for (int i = 0; i < warmups; ++i) {
        auto unused = calculate();
        volatile size_t retained =
#ifdef MASPY
            unused.size();
#else
            unused.f.size();
#endif
        (void)retained;
    }
    auto start = std::chrono::steady_clock::now();
    auto result = calculate();
    double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
    rusage usage{};
    getrusage(RUSAGE_SELF, &usage);
    long peak_rss = usage.ru_maxrss;
    std::ifstream status("/proc/self/status");
    std::string line;
    while (std::getline(status, line)) {
        if (line.starts_with("VmHWM:")) {
            std::istringstream field(line.substr(6));
            field >> peak_rss;
        }
    }
    std::cerr << std::setprecision(17) << seconds << " " << peak_rss << " " << usage.ru_maxrss << "\n";
#ifdef MASPY
    for (auto& row : result) for (auto& x : row) std::cout << x.val << ' ';
#else
    for (auto& x : result.f) std::cout << x.get() << ' ';
#endif
    std::cout << '\n';
}
