class ApproachingLimit < Scout::Plugin
  def build_report
    log_file_path = '/var/log/app-template.log'
    last_bytes = memory(:last_bytes) || 0
    current_length = `wc -c #{log_file_path}`.split(' ')[0].to_i
    count = 0

    # don't run it the first time
    if (last_bytes > 0 )
      read_length = current_length - last_bytes
      # Check to see if this file was rotated. This occurs when the +current_length+ is less than
      # the +last_run+. Don't return a count if this occured.
      if read_length >= 0
        # finds new content from +last_bytes+ to the end of the file, then just extracts from the recorded
        # +read_length+. This ignores new lines that are added after finding the +current_length+. Those lines
        # will be read on the next run.
        count = `tail -c +#{last_bytes+1} #{log_file_path} | head -c #{read_length} | grep "upload limit" -c`.strip().to_i
      else
        count = nil
      end
    end
    report(:errors => count) if count
    remember(:last_bytes, current_length)
  end
end