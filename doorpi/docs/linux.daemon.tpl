#!/bin/sh
### BEGIN INIT INFO
# Provides:          !package!
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: !package!
# Description:       !project!
### END INIT INFO

. /lib/lsb/init-functions

NAME=!package!
DESC="!project!"
DAEMON=!doorpi_executable!
DOORPI_PATH=!doorpi_path!
DAEMON_ARGS="!daemon_args!"
PIDFILE=!pidfile!
SCRIPTNAME=!daemon_folder!/!daemon_name!

# Exit if the package is not installed
if [ none != "$DAEMON" ] && [ ! -x "$DAEMON" ] ; then
        exit 3
fi

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh
if [ -t 0 ] ; then # Be verbose when called from a terminal
    VERBOSE=yes
fi

do_start_cmd()
{
	status_of_proc "$DAEMON" "$NAME" > /dev/null && return 1
	$DAEMON start $DAEMON_ARGS || return 2
}

do_test_cmd()
{
	status_of_proc "$DAEMON" "$NAME" > /dev/null && return 1
	$DAEMON start $DAEMON_ARGS --test || return 2
}
is_doorpi_running()
{
	status_of_proc "$DAEMON" "$NAME" > /dev/null && return 0
	return 1
}
do_stop_cmd()
{
	status_of_proc "$DAEMON" "$NAME" > /dev/null || return 1
	$DAEMON stop || return 2
	rm -f $PIDFILE
	return 0
}

EX=0
case "$1" in
	start)
		[ "$VERBOSE" != no ] && log_daemon_msg "Starting $DESC" "$NAME"
		do_start_cmd
		case "$?" in
			0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
			2) 
				 [ "$VERBOSE" != no ] && log_end_msg 1 
				 EX=1 ;;
		esac
		;;
	stop)
		[ "$VERBOSE" != no ] && log_daemon_msg "Stopping $DESC" "$NAME"
		do_stop_cmd
		case "$?" in
			0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
			2) 
				 [ "$VERBOSE" != no ] && log_end_msg 1 
				 EX=1 ;;
		esac
		;;
	restart)
		[ "$VERBOSE" != no ] && log_daemon_msg "Restarting $DESC" "$NAME"
		do_stop_cmd
		# issue #132
		echo waiting until !package! is stopped
		sleep 3
		is_doorpi_running
		while [ $? -eq 0 ]; do
			echo !package! is still running - wait one more second
			is_doorpi_running
			sleep 1
		done
		sleep 2
		do_start_cmd
		case "$?" in
			0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
			2) 
				 [ "$VERBOSE" != no ] && log_end_msg 1 
				 EX=1 ;;
		esac
		;;
	status)
		status_of_proc "$DAEMON" "$NAME" && return 0 || return $?
		;;
	*)
		echo "Usage: $SCRIPTNAME {start|stop|status|restart}" >&2
		exit 3
		;;
esac

exit $EX
