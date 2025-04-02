import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/flutter_flow/flutter_flow_widgets.dart';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'manage_data_model.dart';
import 'package:max_driving/singleton.dart';
export 'manage_data_model.dart';

class ManageDataWidget extends StatefulWidget {
  const ManageDataWidget({super.key});

  static String routeName = 'ManageData';
  static String routePath = '/manageData';

  @override
  State<ManageDataWidget> createState() => _ManageDataWidgetState();
}

class _ManageDataWidgetState extends State<ManageDataWidget> {
  final Data data = Data();

  late ManageDataModel _model;

  final scaffoldKey = GlobalKey<ScaffoldState>();

  bool cleanData30 = true;

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => ManageDataModel());
  }

  @override
  void dispose() {
    _model.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: scaffoldKey,
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        automaticallyImplyLeading: false,
        leading: FlutterFlowIconButton(
          borderColor: Colors.transparent,
          borderRadius: 30.0,
          buttonSize: 46.0,
          icon: Icon(
            Icons.arrow_back_rounded,
            color: Color(0xFF14181B),
            size: 25.0,
          ),
          onPressed: () async {
            context.pop();
          },
        ),
        title: Text(
          'Manage Data',
          style: FlutterFlowTheme.of(context).headlineMedium.override(
                fontFamily: 'Outfit',
                letterSpacing: 0.0,
              ),
        ),
        actions: [],
        centerTitle: false,
        elevation: 0.0,
      ),
      body: Column(
        mainAxisSize: MainAxisSize.max,
        children: [
          Padding(
            padding: EdgeInsetsDirectional.fromSTEB(0.0, 12.0, 0.0, 0.0),
            child: Material(
              color: Colors.transparent,
              child: SwitchListTile.adaptive(
                value: _model.switchListTileValue1 ??= true,
                onChanged: (newValue) async {
                  safeSetState(() => _model.switchListTileValue1 = newValue!);

                  cleanData30 = newValue;
                  data.data['cleanData30'] = cleanData30;
                  data.notify();
                },
                title: Text(
                  'Push Notifications',
                  style: FlutterFlowTheme.of(context).bodyLarge.override(
                        fontFamily: 'Plus Jakarta Sans',
                        color: Color(0xFF14181B),
                        fontSize: 16.0,
                        letterSpacing: 0.0,
                        fontWeight: FontWeight.normal,
                        lineHeight: 2.0,
                      ),
                ),
                subtitle: Text(
                  'Receive Push notifications from our application on a semi regular basis.',
                  style: FlutterFlowTheme.of(context).bodyMedium.override(
                        fontFamily: 'Plus Jakarta Sans',
                        color: Color(0xFF8B97A2),
                        fontSize: 14.0,
                        letterSpacing: 0.0,
                        fontWeight: FontWeight.normal,
                      ),
                ),
                tileColor: Colors.white,
                activeColor: Color(0xFF4B39EF),
                activeTrackColor: Color(0x4C4B39EF),
                dense: false,
                controlAffinity: ListTileControlAffinity.trailing,
                contentPadding:
                    EdgeInsetsDirectional.fromSTEB(24.0, 12.0, 24.0, 12.0),
              ),
            ),
          ),
          Material(
            color: Colors.transparent,
            child: SwitchListTile.adaptive(
              value: _model.switchListTileValue2 ??= true,
              onChanged: (newValue) async {
                safeSetState(() => _model.switchListTileValue2 = newValue!);
              },
              title: Text(
                'Email Notifications',
                style: FlutterFlowTheme.of(context).bodyLarge.override(
                      fontFamily: 'Plus Jakarta Sans',
                      color: Color(0xFF14181B),
                      fontSize: 16.0,
                      letterSpacing: 0.0,
                      fontWeight: FontWeight.normal,
                      lineHeight: 2.0,
                    ),
              ),
              subtitle: Text(
                'Receive email notifications from our marketing team about new features.',
                style: FlutterFlowTheme.of(context).bodyMedium.override(
                      fontFamily: 'Plus Jakarta Sans',
                      color: Color(0xFF8B97A2),
                      fontSize: 14.0,
                      letterSpacing: 0.0,
                      fontWeight: FontWeight.normal,
                    ),
              ),
              tileColor: Colors.white,
              activeColor: Color(0xFF4B39EF),
              activeTrackColor: Color(0x4C4B39EF),
              dense: false,
              controlAffinity: ListTileControlAffinity.trailing,
              contentPadding:
                  EdgeInsetsDirectional.fromSTEB(24.0, 12.0, 24.0, 12.0),
            ),
          ),
          Material(
            color: Colors.transparent,
            child: SwitchListTile.adaptive(
              value: _model.switchListTileValue3 ??= true,
              onChanged: (newValue) async {
                safeSetState(() => _model.switchListTileValue3 = newValue!);
              },
              title: Text(
                'Location Services',
                style: FlutterFlowTheme.of(context).bodyLarge.override(
                      fontFamily: 'Plus Jakarta Sans',
                      color: Color(0xFF14181B),
                      fontSize: 16.0,
                      letterSpacing: 0.0,
                      fontWeight: FontWeight.normal,
                      lineHeight: 2.0,
                    ),
              ),
              subtitle: Text(
                'Allow us to track your location, this helps keep track of spending and keeps you safe.',
                style: FlutterFlowTheme.of(context).bodyMedium.override(
                      fontFamily: 'Plus Jakarta Sans',
                      color: Color(0xFF8B97A2),
                      fontSize: 14.0,
                      letterSpacing: 0.0,
                      fontWeight: FontWeight.normal,
                    ),
              ),
              tileColor: Colors.white,
              activeColor: Color(0xFF4B39EF),
              activeTrackColor: Color(0x4C4B39EF),
              dense: false,
              controlAffinity: ListTileControlAffinity.trailing,
              contentPadding:
                  EdgeInsetsDirectional.fromSTEB(24.0, 12.0, 24.0, 12.0),
            ),
          ),
          Padding(
            padding: EdgeInsetsDirectional.fromSTEB(0.0, 24.0, 0.0, 0.0),
            child: FFButtonWidget(
              onPressed: () async {
                context.pop();
              },
              text: 'Apply Changes',
              options: FFButtonOptions(
                width: 190.0,
                height: 50.0,
                padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 0.0),
                iconPadding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 0.0),
                color: Color(0xFFCCCCCC),
                textStyle: FlutterFlowTheme.of(context).titleSmall.override(
                      fontFamily: 'Plus Jakarta Sans',
                      color: Color(0xFF4B39EF),
                      fontSize: 16.0,
                      letterSpacing: 0.0,
                      fontWeight: FontWeight.w500,
                    ),
                elevation: 3.0,
                borderSide: BorderSide(
                  color: Colors.transparent,
                  width: 1.0,
                ),
                borderRadius: BorderRadius.circular(30.0),
              ),
            ),
          ),
          Padding(
            padding: EdgeInsetsDirectional.fromSTEB(0.0, 10.0, 0.0, 0.0),
            child: FFButtonWidget(
              onPressed: () {
                print('Button pressed ...');
              },
              text: 'Apply and Exit',
              options: FFButtonOptions(
                width: 190.0,
                height: 50.0,
                padding: EdgeInsetsDirectional.fromSTEB(16.0, 0.0, 16.0, 0.0),
                iconPadding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 0.0),
                color: FlutterFlowTheme.of(context).primary,
                textStyle: FlutterFlowTheme.of(context).titleSmall.override(
                      fontFamily: 'Plus Jakarta Sans',
                      color: Colors.white,
                      letterSpacing: 0.0,
                      fontWeight: FontWeight.w500,
                    ),
                elevation: 0.0,
                borderRadius: BorderRadius.circular(24.0),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
