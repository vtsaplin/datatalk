class Datatalk < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/vtsaplin/datatalk"
  url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.2.tar.gz"
  sha256 "0855b016588fd9427977a4a0d7821a78c4ca6741204edccfb22df64434a75ff4"
  license "MIT"
  head "https://github.com/vtsaplin/datatalk.git", branch: "main"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/datatalk", "--help"
  end
end
