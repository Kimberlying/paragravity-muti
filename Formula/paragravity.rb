class Paragravity < Formula
  desc "Native, non-invasive parallel multi-account & sandbox manager for Google Antigravity"
  homepage "https://github.com/edison-land/paragravity"
  url "https://github.com/edison-land/paragravity/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "6d28c4b2475c69ee79f3e245ca9367f21c3435487b62e04e786028cff9419656"
  license "MIT"

  depends_on :macos

  def install
    bin.install "bin/paragravity"
    bin.install_symlink "paragravity" => "pgrav"

    # Install zsh completions if present
    if File.exist?("completions/_paragravity")
      zsh_completion.install "completions/_paragravity"
      zsh_completion.install_symlink "_paragravity" => "_pgrav"
    end
  end

  test do
    system "#{bin}/paragravity", "--version"
    system "#{bin}/pgrav", "--version"
  end
end
