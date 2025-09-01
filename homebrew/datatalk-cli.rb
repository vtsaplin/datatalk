class DatatalkCli < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/vtsaplin/datatalk"
  url "https://files.pythonhosted.org/packages/source/d/datatalk-cli/datatalk_cli-0.1.1.tar.gz"
  sha256 "TBD_UPDATE_WITH_SCRIPT"
  license "MIT"
  head "https://github.com/vtsaplin/datatalk.git", branch: "main"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/datatalk-cli", "--help"
  end
end
